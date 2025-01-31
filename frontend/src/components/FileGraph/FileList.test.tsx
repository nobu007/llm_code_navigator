import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import FileList from './FileList';
import { FileNode } from '@/types/types';

const mockFiles: FileNode[] = [
  {
    id: '1',
    name: 'file1.py',
    type: 'file',
    children: [],
  },
  {
    id: '2',
    name: 'file2.py',
    type: 'file',
    children: [],
  },
  {
    id: '3',
    name: 'folder1',
    type: 'directory',
    children: [
      {
        id: '4',
        name: 'file3.py',
        type: 'file',
        children: [],
      },
    ],
  },
];

describe('FileList', () => {
  it('renders file list correctly', () => {
    render(<FileList files={mockFiles} onFileSelect={jest.fn()} />);

    expect(screen.getByText('file1.py')).toBeInTheDocument();
    expect(screen.getByText('file2.py')).toBeInTheDocument();
    expect(screen.getByText('folder1')).toBeInTheDocument();
    expect(screen.getByText('file3.py')).toBeInTheDocument();
  });

  it('calls onFileSelect when a file is clicked', () => {
    const onFileSelect = jest.fn();
    render(<FileList files={mockFiles} onFileSelect={onFileSelect} />);

    fireEvent.click(screen.getByText('file1.py'));
    expect(onFileSelect).toHaveBeenCalledWith(mockFiles[0]);

    fireEvent.click(screen.getByText('file3.py'));
    expect(onFileSelect).toHaveBeenCalledWith(mockFiles[2].children[0]);
  });
});
