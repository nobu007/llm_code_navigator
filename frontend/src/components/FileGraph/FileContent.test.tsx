import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import FileContent from './FileContent';

describe('FileContent', () => {
  it('renders file content correctly when fileName and content are provided', () => {
    const fileName = 'testFile.py';
    const content = 'print("Hello, world!")';

    render(<FileContent fileName={fileName} content={content} />);

    expect(screen.getByText('File Content')).toBeInTheDocument();
    expect(screen.getByText(fileName)).toBeInTheDocument();
    expect(screen.getByText(content)).toBeInTheDocument();
  });

  it('renders loading message when content is null', () => {
    const fileName = 'testFile.py';
    const content = null;

    render(<FileContent fileName={fileName} content={content} />);

    expect(screen.getByText('File Content')).toBeInTheDocument();
    expect(screen.getByText(fileName)).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders message to select a file when fileName is null', () => {
    const fileName = null;
    const content = null;

    render(<FileContent fileName={fileName} content={content} />);

    expect(screen.getByText('File Content')).toBeInTheDocument();
    expect(screen.getByText('Select a file to view its content')).toBeInTheDocument();
  });
});
