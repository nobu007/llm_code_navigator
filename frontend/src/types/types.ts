// @/types/types.ts

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

export interface PmdViolation {
  rule: string
  priority: number
  message: string
  line: number
  column: number
}

export interface PmdResult {
  violations: PmdViolation[]
  summary: {
    totalViolations: number
    fileAnalyzed: string
    pmdVersion?: string
    timestamp?: string
  }
}

// Relationship型をエクスポートする
export type Relationship = FileEdge;