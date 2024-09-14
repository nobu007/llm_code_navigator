import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl, useLoadGraph, useRegisterEvents } from '@react-sigma/core';
import '@react-sigma/core/lib/react-sigma.min.css';
import { LayoutForceAtlas2Control } from '@react-sigma/layout-forceatlas2';
import Graph from 'graphology';
import { useEffect } from 'react';

const GraphComponent = () => {
  const LoadGraph = () => {
    const loadGraph = useLoadGraph();
    const registerEvents = useRegisterEvents();

    useEffect(() => {
      const graph = new Graph();

      // Add nodes
      graph.addNode('A', { x: 0, y: 0, size: 10, label: 'Node A', color: '#6c757d' });
      graph.addNode('B', { x: 1, y: 1, size: 10, label: 'Node B', color: '#6c757d' });
      graph.addNode('C', { x: -1, y: -1, size: 10, label: 'Node C', color: '#6c757d' });

      // Add edges
      graph.addEdge('A', 'B');
      graph.addEdge('B', 'C');
      graph.addEdge('C', 'A');

      loadGraph(graph);

      // Optional: Register events
      registerEvents({
        clickNode: (event) => console.log('Clicked node: ', event.node),
        clickEdge: (event) => console.log('Clicked edge: ', event.edge),
      });
    }, [loadGraph, registerEvents]);

    return null;
  };

  return (
    <SigmaContainer style={{ height: '500px', width: '100%' }}>
      <LoadGraph />
      <ControlsContainer position={'bottom-right'}>
        <ZoomControl />
        <FullScreenControl />
        <LayoutForceAtlas2Control />
      </ControlsContainer>
    </SigmaContainer>
  );
};

export default GraphComponent;