export interface FileNode {
  id: string
  label: string
}

export interface FileEdge {
  source: string
  target: string
}

export interface FileData {
  nodes: FileNode[]
  edges: FileEdge[]
}