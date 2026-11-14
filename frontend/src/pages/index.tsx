// import { Layout } from '@/components/layout/Layout';
import React from "react";

import { useFileSystem } from "@/hooks/useFileSystem";

import Layout from "@/components/layout/Layout";

const Home: React.FC = () => {
        const { fileSystem, loading, error, getFileContent, getPmdResult } = useFileSystem();

	console.log("Home component state:", { loading, error, fileSystem }); // デバッグログ

	if (loading) {
		return <div>Loading file system data...</div>;
	}

	if (error) {
		return <div>Error: {error.message}</div>;
	}

	if (!fileSystem) {
		return <div>No file system data available</div>;
	}

	console.log("FileSystem data:", JSON.stringify(fileSystem, null, 2)); // 詳細なデバッグログ

        return <Layout fileSystem={fileSystem} getFileContent={getFileContent} getPmdResult={getPmdResult} />;
};

export default Home;
