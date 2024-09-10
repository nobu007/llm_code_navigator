'use client'

import Head from 'next/head'
import Layout from '@/components/layout/Layout'
import FileGraph from '@/components/FileGraph/FileGraph'

export function SrcPagesIndex() {
  return (
    <>
      <Head>
        <title>Python Files Graph Viewer</title>
        <meta name="description" content="View and explore Python files as a graph" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Layout>
        <main className="flex-grow container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-6">Python Files Graph Viewer</h1>
          <FileGraph />
        </main>
      </Layout>
    </>
  )
}