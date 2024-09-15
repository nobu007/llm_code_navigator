// import { Layout } from '@/components/layout/Layout';
import Layout from "@/components/layout/Layout";
import { useFileSystem } from "@/hooks/useFileSystem";
import React from "react";

const Home: React.FC = () => {
	const { fileSystem, loading, error, getFileContent } = useFileSystem();

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

	return <Layout fileSystem={fileSystem} getFileContent={getFileContent} />;
};

export default Home;
