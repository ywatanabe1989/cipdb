#!/usr/bin/env python3
'''Test suite for cipdb package.'''

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import cipdb


class TestCipdbCore:
    '''Test core cipdb functionality.'''
    
    def setup_method(self):
        '''Reset state before each test.'''
        cipdb.enable()
        # Clear relevant environment variables
        for key in ['CIPDB', 'CIPDB_ID', 'CIPDB_RUNNER_ID', 'DEBUG']:
            os.environ.pop(key, None)
    
    def teardown_method(self):
        '''Clean up after each test.'''
        for key in ['CIPDB', 'CIPDB_ID', 'CIPDB_RUNNER_ID', 'DEBUG']:
            os.environ.pop(key, None)
    
    @patch('ipdb.set_trace')
    def test_simple_true_false(self, mock_ipdb):
        '''Test basic True/False conditions.'''
        cipdb.set_trace(True)
        assert mock_ipdb.called
        
        mock_ipdb.reset_mock()
        cipdb.set_trace(False)
        assert not mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_breakpoint_id_matching(self, mock_ipdb):
        '''Test ID-based breakpoint matching.'''
        # Set runner ID
        os.environ['CIPDB_RUNNER_ID'] = 'test-point'
        
        # Should trigger - IDs match
        cipdb.set_trace(breakpoint_id='test-point')
        assert mock_ipdb.called
        
        # Should not trigger - IDs don't match
        mock_ipdb.reset_mock()
        cipdb.set_trace(breakpoint_id='other-point')
        assert not mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_runner_id_parameter(self, mock_ipdb):
        '''Test explicit runner_id parameter.'''
        # Should trigger when IDs match
        cipdb.set_trace(breakpoint_id='point-a', runner_id='point-a')
        assert mock_ipdb.called
        
        # Should not trigger when IDs don't match
        mock_ipdb.reset_mock()
        cipdb.set_trace(breakpoint_id='point-a', runner_id='point-b')
        assert not mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_no_id_always_triggers(self, mock_ipdb):
        '''Test that breakpoints without IDs always trigger.'''
        # Even with runner ID set, non-ID breakpoints should work
        os.environ['CIPDB_RUNNER_ID'] = 'some-id'
        
        cipdb.set_trace(True)
        assert mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_env_var_condition(self, mock_ipdb):
        '''Test environment variable conditions.'''
        # Check for truthy env var
        cipdb.set_trace("DEBUG")
        assert not mock_ipdb.called
        
        os.environ['DEBUG'] = 'true'
        cipdb.set_trace("DEBUG")
        assert mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_env_var_equality(self, mock_ipdb):
        '''Test environment variable equality check.'''
        os.environ['ENV'] = 'production'
        
        cipdb.set_trace("ENV=development")
        assert not mock_ipdb.called
        
        cipdb.set_trace("ENV=production")
        assert mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_callable_condition(self, mock_ipdb):
        '''Test callable conditions.'''
        x = 5
        cipdb.set_trace(lambda: x > 10)
        assert not mock_ipdb.called
        
        x = 15
        cipdb.set_trace(lambda: x > 10)
        assert mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_global_disable(self, mock_ipdb):
        '''Test global disable/enable.'''
        cipdb.disable()
        cipdb.set_trace(True)
        assert not mock_ipdb.called
        
        cipdb.enable()
        cipdb.set_trace(True)
        assert mock_ipdb.called
    
    @patch('ipdb.set_trace')
    def test_cipdb_env_override(self, mock_ipdb):
        '''Test CIPDB environment variable override.'''
        os.environ['CIPDB'] = 'false'
        cipdb.set_trace(True)
        assert not mock_ipdb.called
        
        os.environ['CIPDB'] = '0'
        cipdb.set_trace(True)
        assert not mock_ipdb.called
        
        os.environ['CIPDB'] = 'off'
        cipdb.set_trace(True)
        assert not mock_ipdb.called
        
        os.environ.pop('CIPDB')
        cipdb.set_trace(True)
        assert mock_ipdb.called
    
    @patch('ipdb.post_mortem')
    def test_post_mortem(self, mock_pm):
        '''Test post_mortem functionality.'''
        try:
            raise ValueError("test")
        except:
            cipdb.post_mortem(condition=True)
            assert mock_pm.called
            
            mock_pm.reset_mock()
            cipdb.post_mortem(condition=False)
            assert not mock_pm.called
    
    @patch('ipdb.post_mortem')
    def test_post_mortem_with_id(self, mock_pm):
        '''Test post_mortem with breakpoint ID.'''
        os.environ['CIPDB_RUNNER_ID'] = 'error-handler'
        
        try:
            raise ValueError("test")
        except:
            cipdb.post_mortem(breakpoint_id='error-handler')
            assert mock_pm.called
            
            mock_pm.reset_mock()
            cipdb.post_mortem(breakpoint_id='other-handler')
            assert not mock_pm.called


class TestCipdbFallback:
    '''Test fallback behavior.'''
    
    @patch('pdb.set_trace')
    def test_fallback_to_pdb(self, mock_pdb):
        '''Test fallback to pdb when ipdb is not available.'''
        # This would require mocking the import system
        # In practice, the code handles ImportError
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
