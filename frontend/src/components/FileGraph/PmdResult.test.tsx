import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import PmdResult from './PmdResult';
import { PmdResult as PmdResultType } from '@/types/types';

describe('PmdResult', () => {
  it('renders PMD result with violations', () => {
    const result: PmdResultType = {
      violations: [
        {
          rule: 'TestRule',
          priority: 3,
          message: 'Test violation message',
          line: 10,
          column: 5
        }
      ],
      summary: {
        totalViolations: 1,
        fileAnalyzed: '/path/to/test.java',
        pmdVersion: '6.55.0'
      }
    };
    
    render(<PmdResult result={result} />);
    expect(screen.getByText('PMD Analysis')).toBeInTheDocument();
    expect(screen.getByText('Summary')).toBeInTheDocument();
    expect(screen.getByText('/path/to/test.java')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('TestRule')).toBeInTheDocument();
    expect(screen.getByText('Test violation message')).toBeInTheDocument();
  });

  it('renders PMD result with no violations', () => {
    const result: PmdResultType = {
      violations: [],
      summary: {
        totalViolations: 0,
        fileAnalyzed: '/path/to/test.java'
      }
    };
    
    render(<PmdResult result={result} />);
    expect(screen.getByText('PMD Analysis')).toBeInTheDocument();
    expect(screen.getByText('No violations found! 🎉')).toBeInTheDocument();
  });

  it('renders placeholder when result is null', () => {
    render(<PmdResult result={null} />);
    expect(screen.getByText('PMD Analysis')).toBeInTheDocument();
    expect(screen.getByText('No analysis available')).toBeInTheDocument();
  });
});
