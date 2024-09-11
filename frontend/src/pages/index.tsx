import FileGraph from '@/components/FileGraph/FileGraph';
import FileList from '@/components/FileGraph/FileList'; // FileListコンポーネントをインポート
import Layout from '@/components/layout/Layout';
import Head from 'next/head';
import React, { useState } from 'react';

const Home: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const handleFileSelect = (fileName: string) => {
    setSelectedFile(fileName)
  }

  return (
    <>
      <Head>
        <title>LLM Code Navigator</title>
        <meta name="description" content="Navigate and explore code with LLM assistance" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Layout>
        <main className="flex-grow container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-6">LLM Code Navigator</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-semibold mb-4">File Structure</h2>
              <FileList onFileSelect={handleFileSelect} />
            </div>
            <div>
              <h2 className="text-2xl font-semibold mb-4">File Graph</h2>
              <FileGraph />
            </div>
          </div>
          {selectedFile && (
            <div className="mt-8">
              <h2 className="text-2xl font-semibold mb-4">Selected File: {selectedFile}</h2>
              {/* ここにファイルの内容を表示するコンポーネントを追加 */}
            </div>
          )}
        </main>
      </Layout>
    </>
  )
}

export default Home