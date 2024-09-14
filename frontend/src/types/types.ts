export interface FileNode {
  id: string
  name: string
  type: 'file' | 'directory'
  children?: FileNode[]
}

export interface FileEdge {
  source: string
  target: string
}

export interface FileData {
  files: FileNode[]
  relationships: FileEdge[]
}