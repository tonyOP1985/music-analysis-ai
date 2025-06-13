import subprocess
import os
import json
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicProcessor:
    def __init__(self, audiveris_path: str = "/app/audiveris"):
        self.audiveris_path = Path(audiveris_path)
        self.audiveris_jar = self.audiveris_path / "lib" / "audiveris.jar"
        
        # Check if Audiveris is properly installed
        if not self.audiveris_jar.exists():
            # Try alternative path
            self.audiveris_jar = self.audiveris_path / "audiveris.jar"
            if not self.audiveris_jar.exists():
                raise FileNotFoundError(f"Audiveris JAR not found at {self.audiveris_jar}")
        
        logger.info(f"Audiveris JAR found at: {self.audiveris_jar}")
    
    def process_pdf(self, pdf_path: str, output_dir: str, 
                   export_formats: list = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process a PDF sheet music file through Audiveris
        
        Args:
            pdf_path: Path to input PDF
            output_dir: Directory for output files
            export_formats: List of export formats ['xml', 'mid', 'pdf']
        
        Returns:
            Tuple of (success, message, metadata)
        """
        if export_formats is None:
            export_formats = ['xml', 'mid']  # MusicXML and MIDI
        
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        
        # Validate input
        if not pdf_path.exists():
            return False, f"Input PDF not found: {pdf_path}", {}
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare Audiveris command
        cmd = [
            'java',
            '-Xmx2g',  # Allocate 2GB memory
            '-jar', str(self.audiveris_jar),
            '-batch',
            '-export'
        ]
        
        # Add export formats
        for fmt in export_formats:
            cmd.extend(['-export', fmt])
        
        # Add output directory and input file
        cmd.extend([
            '-output', str(output_dir),
            str(pdf_path)
        ])
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            # Run Audiveris
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout
                cwd=str(self.audiveris_path)
            )
            
            success = result.returncode == 0
            message = result.stdout if success else result.stderr
            
            # Collect metadata about generated files
            metadata = self._collect_output_metadata(output_dir, pdf_path.stem)
            
            if success:
                logger.info(f"Successfully processed {pdf_path.name}")
                logger.info(f"Generated files: {list(metadata.get('files', {}).keys())}")
            else:
                logger.error(f"Failed to process {pdf_path.name}: {message}")
            
            return success, message, metadata
            
        except subprocess.TimeoutExpired:
            error_msg = "Processing timeout (5 minutes exceeded)"
            logger.error(error_msg)
            return False, error_msg, {}
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, {}
    
    def _collect_output_metadata(self, output_dir: Path, base_name: str) -> Dict[str, Any]:
        """Collect metadata about generated files"""
        metadata = {
            'files': {},
            'base_name': base_name,
            'output_dir': str(output_dir)
        }
        
        # Common file extensions Audiveris generates
        extensions = ['.xml', '.mid', '.pdf', '.omr']
        
        for ext in extensions:
            file_path = output_dir / f"{base_name}{ext}"
            if file_path.exists():
                metadata['files'][ext] = {
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'exists': True
                }
        
        return metadata
    
    def batch_process(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Process multiple PDF files in a directory"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        results = {
            'successful': [],
            'failed': [],
            'total': 0
        }
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        results['total'] = len(pdf_files)
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Create individual output directory
            file_output_dir = output_dir / pdf_file.stem
            
            success, message, metadata = self.process_pdf(
                str(pdf_file), 
                str(file_output_dir)
            )
            
            result_info = {
                'file': pdf_file.name,
                'success': success,
                'message': message,
                'metadata': metadata
            }
            
            if success:
                results['successful'].append(result_info)
            else:
                results['failed'].append(result_info)
        
        return results

def main():
    """Main function for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process sheet music PDFs with Audiveris')
    parser.add_argument('input', help='Input PDF file or directory')
    parser.add_argument('output', help='Output directory')
    parser.add_argument('--batch', action='store_true', help='Process directory of PDFs')
    
    args = parser.parse_args()
    
    try:
        processor = MusicProcessor()
        
        if args.batch:
            results = processor.batch_process(args.input, args.output)
            print(f"\nBatch processing complete:")
            print(f"Total files: {results['total']}")
            print(f"Successful: {len(results['successful'])}")
            print(f"Failed: {len(results['failed'])}")
            
            if results['failed']:
                print("\nFailed files:")
                for failed in results['failed']:
                    print(f"  - {failed['file']}: {failed['message']}")
        else:
            success, message, metadata = processor.process_pdf(args.input, args.output)
            print(f"Success: {success}")
            print(f"Message: {message}")
            print(f"Generated files: {list(metadata.get('files', {}).keys())}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
