import FileGraph from '@/components/FileGraph/FileGraph'
import Layout from '@/components/layout/Layout'
import Head from 'next/head'
import React from 'react'

const Home: React.FC = () => {
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
          <FileGraph />
        </main>
      </Layout>
    </>
  )
}

export default Home