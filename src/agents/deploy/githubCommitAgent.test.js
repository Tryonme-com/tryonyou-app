import { test, describe } from 'node:test';
import assert from 'node:assert';
import { formatSuperCommit, validateBranchName } from './githubCommitAgent.js';

describe('githubCommitAgent', () => {
  describe('formatSuperCommit()', () => {
    test('should format standard commit message correctly', () => {
      const input = {
        version: 'v10.1',
        modules: ['Auth', 'UI'],
        description: 'Fix login issue'
      };
      const result = formatSuperCommit(input);

      assert.ok(result.includes('🔥 TRYONYOU v10.1: Fix login issue'));
      assert.ok(result.includes('✅ Auth'));
      assert.ok(result.includes('✅ UI'));
      assert.ok(result.includes('🌐 Destino: tryonyou.app'));
      assert.ok(result.includes('📋 Patente: PCT/EP2025/067317'));
    });

    test('should handle empty modules array', () => {
      const input = {
        version: 'v1.0',
        modules: [],
        description: 'No modules'
      };
      const result = formatSuperCommit(input);

      assert.ok(result.includes('🔥 TRYONYOU v1.0: No modules'));
      // Should not contain any ✅ lines
      assert.strictEqual(result.includes('✅'), false);
    });

    test('should maintain expected structure', () => {
      const input = {
        version: '1.2.3',
        modules: ['Test'],
        description: 'Desc'
      };
      const result = formatSuperCommit(input);
      const lines = result.split('\n');

      assert.strictEqual(lines[0], '🔥 TRYONYOU 1.2.3: Desc');
      assert.strictEqual(lines[1], '');
      assert.strictEqual(lines[2], '✅ Test');
      assert.strictEqual(lines[3], '');
      assert.strictEqual(lines[4], '🌐 Destino: tryonyou.app');
      assert.strictEqual(lines[5], '📋 Patente: PCT/EP2025/067317');
    });
  });

  describe('validateBranchName()', () => {
    test('should return valid for correct branch names', () => {
      const branches = ['feature/login', 'fix-123', 'main', 'release_v1'];
      branches.forEach(branch => {
        const result = validateBranchName(branch);
        assert.strictEqual(result.valid, true);
        assert.strictEqual(result.suggestion, branch);
      });
    });

    test('should return invalid for branch names with spaces or special characters', () => {
      const input = 'feature login!';
      const result = validateBranchName(input);

      assert.strictEqual(result.valid, false);
      assert.strictEqual(result.suggestion, 'feature-login-');
    });

    test('should handle leading/trailing illegal characters', () => {
      const input = '@feature#';
      const result = validateBranchName(input);

      assert.strictEqual(result.valid, false);
      assert.strictEqual(result.suggestion, '-feature-');
    });
  });
});
