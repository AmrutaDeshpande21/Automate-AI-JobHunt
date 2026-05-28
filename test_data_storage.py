"""
Automated unit tests for Phase 4: Data Storage (CSV Schema, Appending, and Deduplication)
"""

import unittest
import os
import shutil
import pandas as pd
from datetime import datetime
from src.agent.job_agent import JobAgent

class TestDataStorage(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create a sandboxed output directory for testing
        cls.test_dir = os.path.join('data', 'test_runs')
        if not os.path.exists(cls.test_dir):
            os.makedirs(cls.test_dir)
            
    @classmethod
    def tearDownClass(cls):
        # Clean up sandboxed test directory
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        # Initialize job agent targeting the test directory
        self.agent = JobAgent(output_dir=self.test_dir)
        
        # Define mock job listings
        self.mock_jobs_1 = [
            {
                'title': 'Frontend Developer',
                'company': 'Tech Corp',
                'location': 'Bangalore',
                'description': 'React developer role',
                'link': 'https://techcorp.com/jobs/1',
                'source': 'Naukri',
                'scraped_date': '2026-05-28 12:00:00'
            },
            {
                'title': 'Backend Developer',
                'company': 'Cloud Inc',
                'location': 'Mumbai',
                'description': 'Django developer role',
                'link': 'https://cloudinc.com/jobs/2',
                'source': 'RemoteOK',
                'scraped_date': '2026-05-28 12:05:00'
            }
        ]
        
        # Duplicate job (same title, company, location but different date/desc)
        self.mock_jobs_duplicate = [
            {
                'title': 'Frontend Developer',
                'company': 'Tech Corp',
                'location': 'Bangalore',
                'description': 'React developer role - Updated description',
                'link': 'https://techcorp.com/jobs/1-updated',
                'source': 'Naukri',
                'scraped_date': '2026-05-28 13:00:00'
            }
        ]
        
        # New job
        self.mock_jobs_new = [
            {
                'title': 'Data Scientist',
                'company': 'Data Solutions',
                'location': 'Pune',
                'description': 'Machine learning role',
                'link': 'https://datasolutions.com/jobs/3',
                'source': 'Wellfound',
                'scraped_date': '2026-05-28 12:10:00'
            }
        ]

    def test_schema_definition_and_file_creation(self):
        """Test if the file is successfully created with correct schema and order"""
        self.agent.processed_jobs = self.mock_jobs_1
        filename = 'test_schema.csv'
        filepath = self.agent.save_to_csv(filename=filename, append=False)
        
        self.assertTrue(os.path.exists(filepath))
        
        # Load and verify schema
        df = pd.read_csv(filepath, keep_default_na=False)
        expected_cols = [
            'title', 'company', 'location', 'description', 
            'link', 'source', 'scraped_date'
        ]
        
        # Check that all expected columns are present and in order
        self.assertEqual(list(df.columns)[:7], expected_cols)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['title'], 'Frontend Developer')
        self.assertEqual(df.iloc[1]['company'], 'Cloud Inc')

    def test_data_appending_without_duplicates(self):
        """Test appending new unique jobs to an existing file"""
        # Step 1: Write first batch
        self.agent.processed_jobs = self.mock_jobs_1
        filename = 'test_append.csv'
        self.agent.save_to_csv(filename=filename, append=False)
        
        # Step 2: Append second batch (unique new job)
        self.agent.processed_jobs = self.mock_jobs_new
        self.agent.save_to_csv(filename=filename, append=True)
        
        # Load and verify
        filepath = os.path.join(self.test_dir, filename)
        df = pd.read_csv(filepath, keep_default_na=False)
        
        self.assertEqual(len(df), 3)
        self.assertTrue(any(df['title'] == 'Data Scientist'))

    def test_deduplication_on_append(self):
        """Test that duplicate jobs are successfully filtered out during append operations"""
        # Step 1: Write first batch
        self.agent.processed_jobs = self.mock_jobs_1
        filename = 'test_dedup.csv'
        self.agent.save_to_csv(filename=filename, append=False)
        
        # Step 2: Append duplicate job (same title, company, location)
        self.agent.processed_jobs = self.mock_jobs_duplicate
        self.agent.save_to_csv(filename=filename, append=True)
        
        # Load and verify: should still be 2 entries because the duplicate is removed
        filepath = os.path.join(self.test_dir, filename)
        df = pd.read_csv(filepath, keep_default_na=False)
        
        self.assertEqual(len(df), 2)
        # Should keep the first entry (original date and link)
        tech_corp_job = df[df['company'] == 'Tech Corp'].iloc[0]
        self.assertEqual(tech_corp_job['link'], 'https://techcorp.com/jobs/1')

    def test_missing_and_extra_fields(self):
        """Test how the schema handles jobs with missing fields or extra attributes"""
        jobs_irregular = [
            {
                'title': 'DevOps Engineer',
                'company': 'Ops Team',
                # location is missing
                'link': 'https://opsteam.com/jobs/4',
                'source': 'RemoteOK',
                'extra_attribute': 'Should be stripped or ignored'
            }
        ]
        
        self.agent.processed_jobs = jobs_irregular
        filename = 'test_irregular.csv'
        filepath = self.agent.save_to_csv(filename=filename, append=False)
        
        df = pd.read_csv(filepath, keep_default_na=False)
        expected_cols = [
            'title', 'company', 'location', 'description', 
            'link', 'source', 'scraped_date'
        ]
        
        # Verify columns match standard schema
        self.assertEqual(list(df.columns), expected_cols)
        self.assertEqual(df.iloc[0]['location'], 'N/A') # Filled with N/A
        self.assertEqual(df.iloc[0]['description'], 'N/A') # Filled with N/A
        self.assertNotIn('extra_attribute', df.columns) # Extra columns removed

if __name__ == '__main__':
    unittest.main()
