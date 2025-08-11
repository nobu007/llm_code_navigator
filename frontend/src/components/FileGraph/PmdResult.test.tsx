import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import PmdResult from './PmdResult';

describe('PmdResult', () => {
  it('renders PMD result when provided', () => {
    const result = '{"files": []}';
    render(<PmdResult result={result} />);
    expect(screen.getByText('PMD Analysis')).toBeInTheDocument();
    expect(screen.getByText(result)).toBeInTheDocument();
  });

  it('renders placeholder when result is null', () => {
    render(<PmdResult result={null} />);
    expect(screen.getByText('PMD Analysis')).toBeInTheDocument();
    expect(screen.getByText('No analysis available')).toBeInTheDocument();
  });
});
