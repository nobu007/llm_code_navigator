import { FileData, FileNode } from '@/types/types'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'
import { Box, HStack, IconButton, Tab, TabList, TabPanel, TabPanels, Tabs, Text, VStack, useColorMode, useColorModeValue } from "@chakra-ui/react"
import dynamic from 'next/dynamic'
import React, { useEffect, useState } from 'react'

const DynamicFileList = dynamic(() => import('@/components/FileGraph/DynamicFileList'), {
  ssr: false,
  loading: () => <p>Loading file list...</p>
})

const DynamicFileGraph = dynamic(() => import('@/components/FileGraph/DynamicFileGraph'), {
  ssr: false,
  loading: () => <p>Loading file graph...</p>
})

const DynamicFileContent = dynamic(() => import('@/components/FileGraph/DynamicFileContent'), {
  ssr: false,
  loading: () => <p>Loading file content...</p>
})

interface LayoutProps {
  fileSystem: FileData
  getFileContent: (path: string) => Promise<string>
}

const Layout: React.FC<LayoutProps> = ({ fileSystem, getFileContent }) => {
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const { colorMode, toggleColorMode } = useColorMode()
  const bgColor = useColorModeValue("gray.50", "gray.900")
  const color = useColorModeValue("gray.900", "gray.50")
  const [activeTab, setActiveTab] = useState(0)

  const handleFileSelect = async (file: FileNode) => {
    setSelectedFile(file)
    setActiveTab(0) // Switch to Contents tab
    try {
      const content = await getFileContent(file.name)
      setFileContent(content)
    } catch (error) {
      console.error('Error fetching file content:', error)
      setFileContent('Error loading file content')
    }
  }

  useEffect(() => {
    if (activeTab === 1) {
      const graphComponent = document.querySelector('.sigma-container')
      if (graphComponent) {
        graphComponent.dispatchEvent(new Event('resize'))
      }
    }
  }, [activeTab])

  if (!fileSystem || !fileSystem.files || fileSystem.files.length === 0) {
    return (
      <Box bg={bgColor} color={color} minH="100vh" display="flex" alignItems="center" justifyContent="center">
        <Text fontSize="xl">No files found in the backend folder.</Text>
      </Box>
    )
  }

  return (
    <Box bg={bgColor} color={color} minH="100vh">
      <VStack spacing={4} align="stretch" p={4}>
        <HStack justifyContent="space-between">
          <Box fontSize="2xl" fontWeight="bold">LLM Code Navigator</Box>
          <IconButton
            icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            onClick={toggleColorMode}
            aria-label="Toggle color mode"
          />
        </HStack>
        <HStack align="stretch" spacing={4} height="calc(100vh - 100px)">
          <Box width="300px" overflowY="auto" borderWidth={1} borderRadius="md" p={2}>
            <DynamicFileList files={fileSystem.files} onFileSelect={handleFileSelect} />
          </Box>
          <Box flex={1}>
            <Tabs isFitted variant="enclosed" index={activeTab} onChange={(index) => setActiveTab(index)}>
              <TabList mb="1em">
                <Tab>File Content</Tab>
                <Tab>File Graph</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <DynamicFileContent fileName={selectedFile?.name || null} content={fileContent} />
                </TabPanel>
                <TabPanel>
                  <DynamicFileGraph fileData={fileSystem} onNodeSelect={handleFileSelect} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        </HStack>
      </VStack>
    </Box>
  )
}

export default Layout