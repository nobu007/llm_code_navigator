import FileGraph from '@/components/FileGraph/FileGraph'
import FileList from '@/components/FileGraph/FileList'
import Layout from '@/components/layout/Layout'
import { useFileSystem } from '@/hooks/useFileSystem'
import React from 'react'

const Home: React.FC = () => {
  const { fileSystem, loading, error, getFileContent } = useFileSystem()

  if (loading) {
    return <div>Loading...</div>
  }

  if (error) {
    return <div>Error: {error.message}</div>
  }

  // fileSystemがnullでないことを確認
  if (!fileSystem) {
    return <div>No file system data available</div>
  }

  console.log('Home component fileSystem:', fileSystem) // デバッグログ

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">LLM Code Navigator</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-semibold mb-4">File Structure</h2>
            <FileList files={fileSystem.files} onFileSelect={getFileContent} />
          </div>
          <div>
            <h2 className="text-2xl font-semibold mb-4">File Graph</h2>
            <FileGraph files={fileSystem.files} relationships={fileSystem.relationships} />
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default Home