"""
ETL Pipeline Orchestration
Main execution flow for processing ML courses
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

from etl.extractors.pdf_extractor import PDFExtractor
from etl.extractors.notebook_extractor import NotebookExtractor
from etl.processors.nlp_processor import NLPProcessor
from etl.processors.code_processor import CodeProcessor
from etl.loaders.database_loader import DatabaseLoader
from etl.loaders.s3_loader import S3Loader

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoursePipeline:
    """Main ETL pipeline orchestrator"""
    
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.notebook_extractor = NotebookExtractor()
        self.nlp_processor = NLPProcessor()
        self.code_processor = CodeProcessor()
        self.db_loader = DatabaseLoader()
        self.s3_loader = S3Loader()
        
    def run(self, course_id: str, source_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the complete ETL pipeline for a course
        
        Args:
            course_id: Unique course identifier
            source_path: Local path to course materials
            dry_run: If True, don't persist to database/S3
            
        Returns:
            Dictionary with pipeline results and output paths
        """
        results = {
            'course_id': course_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'chapters': [],
            'statistics': {
                'total_files': 0,
                'processed_chapters': 0,
                'extracted_figures': 0,
                'extracted_snippets': 0,
                'errors': []
            }
        }
        
        try:
            source_dir = Path(source_path)
            if not source_dir.exists():
                raise FileNotFoundError(f"Source directory not found: {source_path}")
            
            logger.info(f"Starting ETL pipeline for course: {course_id}")
            
            # Step 1: Extract content
            chapters_data = self._extract_phase(source_dir, course_id)
            
            # Step 2: Process and enrich
            chapters_processed = self._process_phase(chapters_data, course_id)
            
            # Step 3: Load to storage and database
            if not dry_run:
                self._load_phase(chapters_processed, course_id)
            
            # Step 4: Generate output
            content_json = self._generate_content_json(chapters_processed, course_id)
            results['chapters'] = chapters_processed
            results['output_file'] = self._save_output(content_json, course_id, dry_run)
            
            logger.info(f"✓ Pipeline completed successfully for course: {course_id}")
            
        except Exception as e:
            logger.error(f"✗ Pipeline failed: {str(e)}")
            results['status'] = 'failed'
            results['error'] = str(e)
            results['statistics']['errors'].append(str(e))
        
        return results
    
    def _extract_phase(self, source_dir: Path, course_id: str) -> List[Dict[str, Any]]:
        """Phase 1: Extract raw content from PDFs and notebooks"""
        logger.info("Phase 1: Extraction")
        
        chapters = []
        chapter_dirs = sorted(source_dir.glob('ch*'))
        
        for chapter_dir in chapter_dirs:
            if not chapter_dir.is_dir():
                continue
            
            chapter_num = chapter_dir.name
            logger.info(f"  Processing {chapter_num}...")
            
            chapter_data = {
                'id': chapter_num,
                'path': str(chapter_dir),
                'raw_text': '',
                'raw_html': '',
                'figures': [],
                'code_blocks': [],
                'metadata': {}
            }
            
            # Extract from PDF
            pdf_files = list(chapter_dir.glob('*.pdf'))
            if pdf_files:
                logger.info(f"    - Extracting PDF: {pdf_files[0].name}")
                pdf_data = self.pdf_extractor.extract(str(pdf_files[0]))
                chapter_data['raw_text'] = pdf_data['text']
                chapter_data['figures'] = pdf_data['figures']
                chapter_data['metadata']['pdf_source'] = pdf_files[0].name
            
            # Extract from Notebook
            notebook_files = list(chapter_dir.glob('*.ipynb'))
            if notebook_files:
                logger.info(f"    - Extracting notebook: {notebook_files[0].name}")
                notebook_data = self.notebook_extractor.extract(str(notebook_files[0]))
                chapter_data['raw_text'] += '\n' + notebook_data['text']
                chapter_data['code_blocks'].extend(notebook_data['code_blocks'])
                chapter_data['metadata']['notebook_source'] = notebook_files[0].name
            
            chapters.append(chapter_data)
        
        logger.info(f"✓ Extracted {len(chapters)} chapters")
        return chapters
    
    def _process_phase(self, chapters: List[Dict[str, Any]], course_id: str) -> List[Dict[str, Any]]:
        """Phase 2: Process and enrich extracted content"""
        logger.info("Phase 2: Processing & Enrichment")
        
        processed = []
        for chapter in chapters:
            logger.info(f"  Processing {chapter['id']}...")
            
            # NLP processing
            summary_en = self.nlp_processor.summarize(chapter['raw_text'], lang='en')
            keywords = self.nlp_processor.extract_keywords(chapter['raw_text'])
            
            # Code processing
            code_snippets = self.code_processor.extract_and_highlight(
                chapter['code_blocks']
            )
            
            processed_chapter = {
                **chapter,
                'title': {'es': '', 'en': chapter['id'].replace('ch', 'Chapter ')},
                'summary': {
                    'es': self.nlp_processor.summarize(chapter['raw_text'], lang='es'),
                    'en': summary_en
                },
                'keywords': keywords,
                'code_snippets': code_snippets,
                'figures': chapter['figures'],  # Enhanced with S3 paths later
                'processed_at': datetime.now().isoformat()
            }
            
            processed.append(processed_chapter)
        
        logger.info(f"✓ Processed {len(processed)} chapters")
        return processed
    
    def _load_phase(self, chapters: List[Dict[str, Any]], course_id: str) -> None:
        """Phase 3: Load to database and cloud storage"""
        logger.info("Phase 3: Loading to Storage")
        
        for chapter in chapters:
            logger.info(f"  Loading {chapter['id']}...")
            
            # Upload figures to S3
            for figure in chapter['figures']:
                s3_key = self.s3_loader.upload_figure(
                    local_path=figure['local_path'],
                    course_id=course_id,
                    chapter_id=chapter['id']
                )
                figure['s3_key'] = s3_key
            
            # Upload code snippets to S3
            for snippet in chapter['code_snippets']:
                s3_key = self.s3_loader.upload_code(
                    content=snippet['source'],
                    course_id=course_id,
                    chapter_id=chapter['id'],
                    language=snippet['language']
                )
                snippet['s3_key'] = s3_key
            
            # Save to database
            chapter_id = self.db_loader.save_chapter(course_id, chapter)
            logger.info(f"    - Saved to DB: {chapter_id}")
        
        logger.info("✓ Loaded all content")
    
    def _generate_content_json(self, chapters: List[Dict[str, Any]], course_id: str) -> Dict[str, Any]:
        """Generate content.json feed for frontend"""
        return {
            'course': {
                'id': course_id,
                'chapters': [
                    {
                        'id': ch['id'],
                        'title': ch['title'],
                        'summary': ch['summary'],
                        'keywords': ch['keywords'],
                        'figures': [
                            {
                                'id': fig.get('id'),
                                's3_key': fig.get('s3_key'),
                                'caption': fig.get('caption', {'es': '', 'en': ''})
                            }
                            for fig in ch['figures']
                        ],
                        'code_snippets': [
                            {
                                'id': snippet.get('id'),
                                'language': snippet['language'],
                                's3_key': snippet.get('s3_key'),
                                'description': snippet.get('description', {'es': '', 'en': ''})
                            }
                            for snippet in ch['code_snippets']
                        ]
                    }
                    for ch in chapters
                ]
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def _save_output(self, content_json: Dict[str, Any], course_id: str, dry_run: bool) -> str:
        """Save output content.json"""
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f'{course_id}-content.json'
        with open(output_file, 'w') as f:
            json.dump(content_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Generated {output_file}")
        return str(output_file)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ML Course ETL Pipeline')
    parser.add_argument('--course-id', required=True, help='Course identifier')
    parser.add_argument('--source', required=True, help='Source directory path')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without persisting')
    
    args = parser.parse_args()
    
    pipeline = CoursePipeline()
    results = pipeline.run(args.course_id, args.source, dry_run=args.dry_run)
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
