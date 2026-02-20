import React, { useState, useEffect, useRef } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
  Alert,
  Animated,
  Dimensions,
  Platform
} from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

type TreeNode = {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
  id: string;
  x?: number;
  y?: number;
};

type Algorithm = 'DFS' | 'BFS';

// Build tree from level-order array using iterative approach
const buildTree = (arr: number[]): TreeNode | null => {
  if (arr.length === 0) return null;
  
  const root: TreeNode = {
    val: arr[0],
    left: null,
    right: null,
    id: Math.random().toString(36).substr(2, 9),
  };
  
  const queue: Array<{ node: TreeNode; index: number }> = [];
  queue.push({ node: root, index: 0 });
  
  while (queue.length > 0) {
    const { node, index } = queue.shift()!;
    
    const leftIndex = 2 * index + 1;
    const rightIndex = 2 * index + 2;
    
    if (leftIndex < arr.length) {
      node.left = {
        val: arr[leftIndex],
        left: null,
        right: null,
        id: Math.random().toString(36).substr(2, 9),
      };
      queue.push({ node: node.left, index: leftIndex });
    }
    
    if (rightIndex < arr.length) {
      node.right = {
        val: arr[rightIndex],
        left: null,
        right: null,
        id: Math.random().toString(36).substr(2, 9),
      };
      queue.push({ node: node.right, index: rightIndex });
    }
  }
  
  return root;
};

// Calculate tree height
const getTreeHeight = (node: TreeNode | null): number => {
  if (!node) return 0;
  return 1 + Math.max(getTreeHeight(node.left), getTreeHeight(node.right));
};

// Calculate total nodes in tree
const getTotalNodes = (node: TreeNode | null): number => {
  if (!node) return 0;
  return 1 + getTotalNodes(node.left) + getTotalNodes(node.right);
};

// Calculate node positions with dynamic adjustments
const calculateNodePositions = (
  root: TreeNode | null,
  containerWidth: number = SCREEN_WIDTH * 0.9
): {
  positions: Map<string, { x: number; y: number }>;
  nodeRadius: number;
  levelHeight: number;
} => {
  const positions = new Map<string, { x: number; y: number }>();
  if (!root) return { positions, nodeRadius: 30, levelHeight: 60 };

  const treeHeight = getTreeHeight(root);
  const totalNodes = getTotalNodes(root);
  
  let baseNodeRadius = 30;
  let baseLevelHeight = 60;
  
  if (totalNodes > 10) {
    baseNodeRadius = Math.max(22, 30 - (totalNodes - 10) * 0.4);
    baseLevelHeight = Math.max(40, 60 - (totalNodes - 10) * 1.2);
  }
  
  if (treeHeight > 5) {
    baseLevelHeight = Math.max(35, baseLevelHeight - (treeHeight - 5) * 2.5);
    baseNodeRadius = Math.max(18, baseNodeRadius - (treeHeight - 5) * 0.8);
  }
  
  const nodeRadius = baseNodeRadius;
  const levelHeight = baseLevelHeight;
  const nodeDiameter = nodeRadius * 2;
  
  const queue: Array<{ node: TreeNode; level: number; minX: number; maxX: number }> = [];
  queue.push({ node: root, level: 0, minX: 0, maxX: containerWidth });

  while (queue.length > 0) {
    const { node, level, minX, maxX } = queue.shift()!;
    
    const x = (minX + maxX) / 2;
    const y = level * levelHeight + nodeRadius + 20;
    
    const margin = nodeRadius + 5;
    const boundedX = Math.max(margin, Math.min(containerWidth - margin, x));
    
    positions.set(node.id, { x: boundedX, y });

    if (node.left || node.right) {
      const availableWidth = maxX - minX;
      const spacingFactor = Math.min(0.45, 0.65 / (level + 1));
      const spacing = availableWidth * spacingFactor;
      
      if (node.left) {
        const leftMaxX = boundedX - spacing / 2;
        if (leftMaxX > minX + nodeDiameter) {
          queue.push({ node: node.left, level: level + 1, minX, maxX: leftMaxX });
        } else {
          queue.push({ node: node.left, level: level + 1, minX: minX + nodeDiameter, maxX: boundedX - nodeDiameter });
        }
      }
      
      if (node.right) {
        const rightMinX = boundedX + spacing / 2;
        if (rightMinX < maxX - nodeDiameter) {
          queue.push({ node: node.right, level: level + 1, minX: rightMinX, maxX });
        } else {
          queue.push({ node: node.right, level: level + 1, minX: boundedX + nodeDiameter, maxX: maxX - nodeDiameter });
        }
      }
    }
  }

  return { positions, nodeRadius, levelHeight };
};

// DFS Preorder Traversal
const dfsPreorder = (root: TreeNode | null): TreeNode[] => {
  const result: TreeNode[] = [];
  
  const dfs = (node: TreeNode | null) => {
    if (!node) return;
    result.push(node);
    dfs(node.left);
    dfs(node.right);
  };
  
  dfs(root);
  return result;
};

// BFS Level Order Traversal
const bfsLevelOrder = (root: TreeNode | null): TreeNode[] => {
  const result: TreeNode[] = [];
  if (!root) return result;

  const queue: TreeNode[] = [root];
  
  while (queue.length > 0) {
    const current = queue.shift()!;
    result.push(current);
    
    if (current.left) queue.push(current.left);
    if (current.right) queue.push(current.right);
  }
  
  return result;
};

// Generate random tree array - maximum 15 nodes
const generateRandomTreeArray = () => {
  const maxNodes = 15;
  const size = Math.floor(Math.random() * (maxNodes - 3)) + 3;
  
  const arr: number[] = [];
  for (let i = 0; i < size; i++) {
    arr.push(Math.floor(Math.random() * 100) + 1);
  }
  return arr;
};

// Parse input string to numbers array, skipping empty values
const parseInputToNumbers = (input: string): number[] => {
  const numbers = input
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)
    .map(s => {
      const num = parseInt(s, 10);
      return isNaN(num) ? 0 : num;
    })
    .filter(num => num > 0)
    .slice(0, 15);
  
  return numbers;
};

// Render tree as text with proper indentation (for mobile/fallback)
const renderTreeText = (node: TreeNode | null, order: TreeNode[], currentIdx: number, prefix = '', isLeft = true): string => {
  if (!node) return '';
  
  let result = '';
  const connector = isLeft ? '└── ' : '├── ';
  const newPrefix = prefix + (isLeft ? '    ' : '│   ');
  
  const idx = order.findIndex(n => n.id === node.id);
  let status = '';
  if (idx === currentIdx) status = ' 🟡';
  else if (idx !== -1 && idx < currentIdx) status = ' ✅';
  
  result += prefix + connector + node.val + status + '\n';
  
  if (node.right) {
    result += renderTreeText(node.right, order, currentIdx, newPrefix, false);
  }
  if (node.left) {
    result += renderTreeText(node.left, order, currentIdx, newPrefix, true);
  }
  
  return result;
};

// Tree Node Component with dynamic sizing (for web/visual view)
const TreeNodeComponent = ({ 
  node, 
  positions, 
  nodeRadius,
  isCurrent, 
  isVisited,
  onNodePress 
}: { 
  node: TreeNode;
  positions: Map<string, {x: number, y: number}>;
  nodeRadius: number;
  isCurrent: boolean;
  isVisited: boolean;
  onNodePress?: (node: TreeNode) => void;
}) => {
  const position = positions.get(node.id);
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const nodeSize = nodeRadius * 2;

  useEffect(() => {
    if (isCurrent) {
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 1.3,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1.1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      scaleAnim.setValue(1);
    }
  }, [isCurrent]);

  if (!position) return null;

  return (
    <TouchableOpacity
      style={[
        styles.treeNode,
        {
          width: nodeSize,
          height: nodeSize,
          borderRadius: nodeRadius,
        },
        isCurrent && styles.currentNode,
        isVisited && styles.visitedNode,
        {
          position: 'absolute',
          left: position.x - nodeRadius,
          top: position.y - nodeRadius,
          zIndex: 10,
        },
      ]}
      onPress={() => onNodePress?.(node)}
      activeOpacity={0.8}
    >
      <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
        <Text style={[
          styles.nodeValueText,
          { fontSize: nodeRadius > 25 ? 16 : nodeRadius > 20 ? 14 : 12 },
          (isCurrent || isVisited) && styles.nodeValueTextActive
        ]}>
          {node.val}
        </Text>
        {(isCurrent || isVisited) && (
          <View style={[
            styles.nodeStatusIndicator,
            { 
              top: -nodeRadius * 0.3, 
              right: -nodeRadius * 0.3,
              borderRadius: nodeRadius * 0.3,
              padding: nodeRadius * 0.1
            }
          ]}>
            <Text style={[
              styles.nodeStatusEmoji,
              { fontSize: nodeRadius > 25 ? 12 : nodeRadius > 20 ? 10 : 8 }
            ]}>
              {isCurrent ? '🟡' : '✅'}
            </Text>
          </View>
        )}
      </Animated.View>
    </TouchableOpacity>
  );
};

// Tree Line Component with dynamic sizing (for web/visual view)
const TreeLineComponent = ({
  startId,
  endId,
  positions,
  lineWidth = 2
}: {
  startId: string;
  endId: string;
  positions: Map<string, {x: number, y: number}>;
  lineWidth?: number;
}) => {
  const startPos = positions.get(startId);
  const endPos = positions.get(endId);
  
  if (!startPos || !endPos) return null;
  
  const dx = endPos.x - startPos.x;
  const dy = endPos.y - startPos.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  
  const adjustedLineWidth = Math.max(1, lineWidth * (1 - distance / 1000));
  
  return (
    <View
      style={[
        styles.treeLine,
        {
          height: adjustedLineWidth,
          backgroundColor: dx === 0 ? '#cbd5e1' : '#94a3b8',
          position: 'absolute',
          left: startPos.x,
          top: startPos.y,
          width: distance,
          transform: [
            { rotate: `${angle}deg` }
          ],
        },
      ]}
    />
  );
};

export function BFSVisualizer() {
  const [input, setInput] = useState('1,2,3,4,5,6,7');
  const [root, setRoot] = useState<TreeNode | null>(null);
  const [order, setOrder] = useState<TreeNode[]>([]);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const [speed, setSpeed] = useState(1000);
  const [isPlaying, setIsPlaying] = useState(false);
  const [nodePositions, setNodePositions] = useState<Map<string, {x: number, y: number}>>(new Map());
  const [nodeRadius, setNodeRadius] = useState(30);
  const [levelHeight, setLevelHeight] = useState(60);
  const [treeContainerWidth, setTreeContainerWidth] = useState(SCREEN_WIDTH * 0.9);
  const [treeHeight, setTreeHeight] = useState(0);
  const [totalNodes, setTotalNodes] = useState(0);
  const [algorithm, setAlgorithm] = useState<Algorithm>('DFS');
  const timer = useRef<NodeJS.Timeout | null>(null);
  const animation = useRef(new Animated.Value(0)).current;
  const treeScrollViewRef = useRef<ScrollView>(null);
  const treeContainerRef = useRef<View>(null);

  useEffect(() => {
    try {
      const numbers = parseInputToNumbers(input);
      
      if (numbers.length === 0) {
        setRoot(null);
        setTotalNodes(0);
        setTreeHeight(0);
        return;
      }
      
      const tree = buildTree(numbers);
      
      if (tree) {
        setRoot(tree);
        resetTraversal();
        
        const height = getTreeHeight(tree);
        const nodes = getTotalNodes(tree);
        setTreeHeight(height);
        setTotalNodes(nodes);
        
        const { positions, nodeRadius: radius, levelHeight: lHeight } = 
          calculateNodePositions(tree, treeContainerWidth);
        setNodePositions(positions);
        setNodeRadius(radius);
        setLevelHeight(lHeight);
        
        setTimeout(() => {
          if (treeScrollViewRef.current && treeContainerRef.current) {
            treeScrollViewRef.current.scrollTo({
              x: Math.max(0, (treeContainerWidth * 0.8 - SCREEN_WIDTH * 0.5) / 2),
              animated: true
            });
          }
        }, 100);
      } else {
        setRoot(null);
        setTotalNodes(0);
        setTreeHeight(0);
      }
    } catch (e) {
      Alert.alert('Error', 'Invalid tree input format');
    }
  }, [input, treeContainerWidth]);

  const handleInputChange = (text: string) => {
    setInput(text);
  };

  const handleInputBlur = () => {
    const numbers = parseInputToNumbers(input);
    
    if (numbers.length > 0) {
      setInput(numbers.join(','));
    } else {
      setInput('1,2,3,4,5,6,7');
    }
  };

  const handleTreeContainerLayout = (event: any) => {
    const { width } = event.nativeEvent.layout;
    const newWidth = Math.max(width, SCREEN_WIDTH * 0.8);
    setTreeContainerWidth(newWidth);
  };

  const startTraversal = () => {
    if (!root || totalNodes === 0) {
      Alert.alert('Invalid Tree', 'Please enter a valid tree with numbers only.');
      return;
    }
    
    let seq: TreeNode[] = [];
    if (algorithm === 'DFS') {
      seq = dfsPreorder(root);
    } else {
      seq = bfsLevelOrder(root);
    }
    
    setOrder(seq);
    setCurrentIdx(-1);
    setIsPlaying(true);
    
    if (timer.current) clearInterval(timer.current);
    
    setTimeout(() => {
      setCurrentIdx(0);
      animateNode();
      timer.current = setInterval(() => {
        setCurrentIdx((i) => {
          if (i + 1 >= seq.length + 1) {
            if (timer.current) clearInterval(timer.current);
            setIsPlaying(false);
            return i;
          }
          animateNode();
          return i + 1;
        });
      }, speed);
    }, 300);
  };

  const animateNode = () => {
    animation.setValue(0);
    Animated.timing(animation, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  };

  const resetTraversal = () => {
    if (timer.current) clearInterval(timer.current);
    setOrder([]);
    setCurrentIdx(-1);
    setIsPlaying(false);
  };

  const generateRandomTree = () => {
    const arr = generateRandomTreeArray();
    setInput(arr.join(','));
  };

  const getSpeedLabel = (speed: number) => {
    if (speed === 250) return '⚡ Fast';
    if (speed === 500) return '🏃 Medium';
    if (speed === 1000) return '🚶 Slow';
    if (speed === 2000) return '🐢 Very Slow';
    return `${speed}ms`;
  };

  const handleNodePress = (node: TreeNode) => {
    Alert.alert(
      'Node Information',
      `Value: ${node.val}\nPosition in traversal: ${
        order.findIndex(n => n.id === node.id) + 1 || 'Not visited yet'
      }`,
      [{ text: 'OK' }]
    );
  };

  const getTreeEdges = (node: TreeNode | null, edges: Array<[string, string]> = []): Array<[string, string]> => {
    if (!node) return edges;
    if (node.left) {
      edges.push([node.id, node.left.id]);
      getTreeEdges(node.left, edges);
    }
    if (node.right) {
      edges.push([node.id, node.right.id]);
      getTreeEdges(node.right, edges);
    }
    return edges;
  };

  const getTreeVisualizationHeight = () => {
    const minHeight = 200;
    const maxHeight = 450;
    const calculatedHeight = treeHeight * levelHeight + nodeRadius * 2 + 40;
    return Math.min(maxHeight, Math.max(minHeight, calculatedHeight));
  };

  const renderTreeNodes = (node: TreeNode | null): React.ReactNode => {
    if (!node) return null;
    
    const isCurrent = order[currentIdx]?.id === node.id;
    const isVisited = order.findIndex(n => n.id === node.id) < currentIdx;

    return (
      <React.Fragment key={node.id}>
        <TreeNodeComponent
          node={node}
          positions={nodePositions}
          nodeRadius={nodeRadius}
          isCurrent={isCurrent}
          isVisited={isVisited}
          onNodePress={handleNodePress}
        />
        {renderTreeNodes(node.left)}
        {renderTreeNodes(node.right)}
      </React.Fragment>
    );
  };

  const renderTreeLines = () => {
    if (!root) return null;
    const edges = getTreeEdges(root);
    
    return edges.map(([parentId, childId], index) => (
      <TreeLineComponent
        key={`${parentId}-${childId}`}
        startId={parentId}
        endId={childId}
        positions={nodePositions}
        lineWidth={Math.max(1, 3 - treeHeight * 0.2)}
      />
    ));
  };

  const renderTreeVisualization = () => {
    if (!root || totalNodes === 0) return null;

    if (Platform.OS === 'web') {
      // Web view - visual tree with lines and nodes
      return (
        <View style={styles.treeCard}>
          <Text style={styles.treeTitle}>Binary Tree Visualization:</Text>
          <View 
            style={styles.treeContainerWrapper}
            onLayout={handleTreeContainerLayout}
          >
            <ScrollView 
              ref={treeScrollViewRef}
              horizontal 
              showsHorizontalScrollIndicator={true}
              style={styles.treeScrollView}
              contentContainerStyle={[
                styles.treeScrollContent,
                { minWidth: Math.max(treeContainerWidth, SCREEN_WIDTH * 0.8) }
              ]}
            >
              <View 
                ref={treeContainerRef}
                style={[
                  styles.treeContainer,
                  { 
                    width: Math.max(treeContainerWidth, SCREEN_WIDTH * 0.8),
                    height: getTreeVisualizationHeight()
                  }
                ]}
              >
                {renderTreeLines()}
                {renderTreeNodes(root)}
              </View>
            </ScrollView>
          </View>
          <Text style={styles.treeHint}>
            💡 Tip: Scroll horizontally to view the entire tree. Tap on nodes for details.
            {treeHeight > 5 && ' (Tree automatically adjusted for better fit)'}
          </Text>
        </View>
      );
    } else {
      // Mobile view - text-based tree (better performance)
      return (
        <View style={styles.treeCard}>
          <Text style={styles.treeTitle}>Tree Structure:</Text>
          <View style={styles.treeContainer}>
            <Text style={styles.treeText}>
              {renderTreeText(root, order, currentIdx)}
            </Text>
          </View>
        </View>
      );
    }
  };

  const getAlgorithmInfo = () => {
    if (algorithm === 'DFS') {
      return {
        title: '📖 About DFS (Depth-First Search):',
        info: [
          '• 🌳 Traversal Order: Root → Left subtree → Right subtree (Preorder)',
          '• 📊 Uses: Stack data structure (LIFO - Last In First Out)',
          '• 🎯 Explores as deep as possible before backtracking',
          '• ⚡ Time Complexity: O(n) where n is number of nodes',
          '• 💾 Space Complexity: O(h) where h is height of tree',
          '• 🔍 Three Types: Preorder, Inorder, Postorder',
          '• 🗺️ Good for path finding and tree/graph exploration',
        ]
      };
    } else {
      return {
        title: '📖 About BFS (Breadth-First Search):',
        info: [
          '• 🔄 Traversal Order: Top → Bottom, Left → Right',
          '• 📊 Uses: Queue data structure (FIFO - First In First Out)',
          '• 🎯 Explores all nodes at current level before moving to next level',
          '• ⚡ Time Complexity: O(n) where n is number of nodes',
          '• 💾 Space Complexity: O(w) where w is maximum width',
          '• 🗺️ Perfect for finding shortest paths in unweighted graphs',
          '• 🔍 Algorithm: Use queue, visit root, add children to queue',
        ]
      };
    }
  };

  const getTraversalPathTitle = () => {
    return algorithm === 'DFS' 
      ? 'DFS Traversal Path (Preorder):'
      : 'BFS Traversal Path (Level Order):';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>
          {algorithm === 'DFS' ? '🌳 DFS Visualizer' : '🔄 BFS Visualizer'}
        </Text>
        <Text style={styles.subtitle}>
          {algorithm === 'DFS' 
            ? 'Preorder Traversal: Root → Left → Right'
            : 'Level Order Traversal: Top → Bottom, Left → Right'}
        </Text>

        <View style={styles.algorithmToggle}>
          <TouchableOpacity
            style={[
              styles.algorithmButton,
              algorithm === 'DFS' && styles.algorithmButtonActive,
              isPlaying && styles.algorithmButtonDisabled
            ]}
            onPress={() => {
              if (!isPlaying) {
                setAlgorithm('DFS');
                resetTraversal();
              }
            }}
            disabled={isPlaying}
          >
            <Text style={[
              styles.algorithmButtonText,
              algorithm === 'DFS' && styles.algorithmButtonTextActive
            ]}>
              🌳 Depth-First Search
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.algorithmButton,
              algorithm === 'BFS' && styles.algorithmButtonActive,
              isPlaying && styles.algorithmButtonDisabled
            ]}
            onPress={() => {
              if (!isPlaying) {
                setAlgorithm('BFS');
                resetTraversal();
              }
            }}
            disabled={isPlaying}
          >
            <Text style={[
              styles.algorithmButtonText,
              algorithm === 'BFS' && styles.algorithmButtonTextActive
            ]}>
              🔄 Breadth-First Search
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Tree Input</Text>
          <Text style={styles.inputHint}>
            Enter numbers only (comma-separated, maximum 15 nodes):
          </Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. 1,2,3,4,5,6,7"
            value={input}
            onChangeText={handleInputChange}
            onBlur={handleInputBlur}
            editable={!isPlaying}
            keyboardType="numbers-and-punctuation"
          />
          {root && totalNodes > 0 && (
            <Text style={styles.treeStats}>
              🌳 Tree: {totalNodes} nodes (Max: 15), Height: {treeHeight} | 
              📏 Auto-size: {Math.round(nodeRadius * 2)}px nodes, {levelHeight}px spacing
            </Text>
          )}
          {parseInputToNumbers(input).length >= 15 && (
            <Text style={styles.warningText}>
              ⚠️ Maximum 15 nodes allowed. Extra nodes will be ignored.
            </Text>
          )}
          {parseInputToNumbers(input).length === 0 && input.length > 0 && (
            <Text style={styles.errorText}>
              ❌ Invalid input. Please enter numbers separated by commas.
            </Text>
          )}
        </View>

        <View style={styles.speedSection}>
          <Text style={styles.speedLabel}>Animation Speed:</Text>
          <View style={styles.speedButtons}>
            {[250, 500, 1000, 2000].map((spd) => (
              <TouchableOpacity
                key={spd}
                style={[
                  styles.speedBtn,
                  speed === spd && styles.speedBtnActive,
                  isPlaying && styles.speedBtnDisabled
                ]}
                onPress={() => setSpeed(spd)}
                disabled={isPlaying}
              >
                <Text style={[
                  styles.speedBtnText,
                  speed === spd && styles.speedBtnTextActive
                ]}>
                  {getSpeedLabel(spd)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.controlButton, styles.startButton, (!root || isPlaying || totalNodes === 0) && styles.buttonDisabled]}
            onPress={startTraversal}
            disabled={!root || isPlaying || totalNodes === 0}
          >
            <Text style={styles.buttonText}>
              ▶️ Start {algorithm}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.resetButton, !isPlaying && currentIdx === -1 && styles.buttonDisabled]}
            onPress={resetTraversal}
            disabled={!isPlaying && currentIdx === -1}
          >
            <Text style={styles.buttonText}>🔄 Reset</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.randomButton, (!root || isPlaying) && styles.buttonDisabled]}
            onPress={generateRandomTree}
          >
            <Text style={styles.buttonText}>🎲 Random Tree</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.status}>
            {currentIdx === -1 ? `Ready to start ${algorithm} traversal` : 
             currentIdx >= order.length ? '✅ Traversal completed!' : 
             `🔍 Visiting node: ${order[currentIdx]?.val}`}
          </Text>
          {order.length > 0 && (
            <Text style={styles.progress}>
              Progress: {Math.min(currentIdx + 1, order.length)}/{order.length} nodes
            </Text>
          )}
        </View>

        {order.length > 0 && (
          <View style={styles.progressCard}>
            <View style={styles.progressBar}>
              <View style={[
                styles.progressFill, 
                { width: `${((Math.min(currentIdx + 1, order.length)) / order.length) * 100}%` }
              ]} />
            </View>
          </View>
        )}

        {renderTreeVisualization()}

        {!root && parseInputToNumbers(input).length > 0 && (
          <View style={styles.errorCard}>
            <Text style={styles.errorCardTitle}>⚠️ Tree Construction Error</Text>
            <Text style={styles.errorCardText}>
              Unable to build tree from input. Please check:
              {"\n"}• All values are valid numbers (1-100)
              {"\n"}• Input format: comma-separated numbers
              {"\n"}• Example: 1,2,3,4,5,6,7
            </Text>
          </View>
        )}

        {order.length > 0 && (
          <View style={styles.traversalCard}>
            <Text style={styles.traversalTitle}>{getTraversalPathTitle()}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.traversalPath}>
                {order.map((node, index) => (
                  <Animated.View 
                    key={node.id} 
                    style={[
                      styles.pathItem,
                      {
                        transform: [
                          {
                            scale: index === currentIdx
                              ? animation.interpolate({
                                  inputRange: [0, 0.5, 1],
                                  outputRange: [1, 1.3, 1.1]
                                })
                              : 1
                          }
                        ]
                      }
                    ]}
                  >
                    <Text style={[
                      styles.nodeValue,
                      index === currentIdx && styles.currentNodeValue,
                      index < currentIdx && styles.visitedNodeValue
                    ]}>
                      {node.val}
                    </Text>
                    {index < order.length - 1 && (
                      <Text style={styles.arrow}>→</Text>
                    )}
                  </Animated.View>
                ))}
              </View>
            </ScrollView>
          </View>
        )}

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendNode, styles.legendCurrent]} />
            <Text style={styles.legendText}>Current node being visited</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendNode, styles.legendVisited]} />
            <Text style={styles.legendText}>Already visited nodes</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={styles.legendNode} />
            <Text style={styles.legendText}>Unvisited nodes</Text>
          </View>
          {Platform.OS === 'web' && (
            <View style={styles.legendItem}>
              <View style={styles.treeLineExample} />
              <Text style={styles.legendText}>Parent-child connection</Text>
            </View>
          )}
        </View>

        <View style={[
          styles.infoCard,
          algorithm === 'DFS' ? styles.infoCardDFS : styles.infoCardBFS
        ]}>
          <Text style={styles.infoTitle}>{getAlgorithmInfo().title}</Text>
          <Text style={styles.infoText}>
            {getAlgorithmInfo().info.join('\n')}
            {'\n'}• ⚠️ Restrictions: Numbers only, maximum 15 nodes
            {'\n'}• ⚙️ Auto-adjust: Node size and spacing adjust based on tree complexity
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const DFS_PRIMARY = '#3b82f6';
const BFS_PRIMARY = '#8b5cf6';
const CURRENT_COLOR = '#f59e0b';
const VISITED_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 24,
    textAlign: 'center',
  },
  algorithmToggle: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 10,
    marginBottom: 20,
  },
  algorithmButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: '#f3f4f6',
    borderWidth: 2,
    borderColor: 'transparent',
    minWidth: 150,
  },
  algorithmButtonActive: {
    backgroundColor: '#e0e7ff',
  },
  algorithmButtonDisabled: {
    opacity: 0.5,
  },
  algorithmButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
    textAlign: 'center',
  },
  algorithmButtonTextActive: {
    color: '#3b82f6',
  },
  inputSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 10,
  },
  inputHint: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  input: {
    height: 50,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
    color: '#1f2937',
  },
  treeStats: {
    fontSize: 12,
    color: '#0ea5e9',
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  warningText: {
    fontSize: 12,
    color: '#f59e0b',
    marginTop: 4,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  errorText: {
    fontSize: 12,
    color: '#ef4444',
    marginTop: 4,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  errorCard: {
    backgroundColor: '#fee2e2',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#ef4444',
  },
  errorCardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#dc2626',
    marginBottom: 8,
    textAlign: 'center',
  },
  errorCardText: {
    fontSize: 14,
    color: '#991b1b',
    lineHeight: 20,
  },
  speedSection: {
    marginBottom: 20,
  },
  speedLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
  },
  speedButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'center',
  },
  speedBtn: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  speedBtnActive: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  speedBtnDisabled: {
    opacity: 0.6,
  },
  speedBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  speedBtnTextActive: {
    color: 'white',
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 20,
  },
  controlButton: {
    flex: 1,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    minWidth: 110,
    ...(Platform.OS === "web" && {
      maxWidth: "20%"
    })
  },
  startButton: {
    backgroundColor: '#3b82f6',
  },
  resetButton: {
    backgroundColor: '#6b7280',
  },
  randomButton: {
    backgroundColor: '#8b5cf6',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  statusContainer: {
    backgroundColor: '#e0e7ff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  status: {
    fontSize: 16,
    fontWeight: '600',
    color: '#3b82f6',
    textAlign: 'center',
    marginBottom: 8,
  },
  progress: {
    fontSize: 14,
    color: '#0ea5e9',
    textAlign: 'center',
  },
  progressCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3b82f6',
    borderRadius: 4,
  },
  treeCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  treeTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#3b82f6',
    textAlign: 'center',
  },
  treeContainerWrapper: {
    minHeight: 200,
  },
  treeScrollView: {
    flex: 1,
  },
  treeScrollContent: {
    paddingVertical: 10,
  },
  treeContainer: {
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    position: 'relative',
    overflow: 'visible',
  },
  treeHint: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 12,
    fontStyle: 'italic',
  },
  // For mobile text-based tree
  treeText: {
    fontSize: 16,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : Platform.OS === 'android' ? 'monospace' : 'monospace',
    lineHeight: 24,
    color: '#1f2937',
  },
  // For web visual tree
  treeNode: {
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#d1d5db',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  currentNode: {
    backgroundColor: CURRENT_COLOR,
    borderColor: '#d97706',
    shadowColor: CURRENT_COLOR,
    shadowOpacity: 0.3,
    elevation: 5,
  },
  visitedNode: {
    backgroundColor: VISITED_COLOR,
    borderColor: '#059669',
  },
  nodeValueText: {
    fontWeight: '700',
    color: '#374151',
  },
  nodeValueTextActive: {
    color: 'white',
  },
  nodeStatusIndicator: {
    position: 'absolute',
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1,
    elevation: 2,
  },
  nodeStatusEmoji: {
    fontSize: 12,
  },
  treeLine: {
    zIndex: 1,
    transformOrigin: '0% 0%',
  },
  traversalCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  traversalTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#3b82f6',
    textAlign: 'center',
  },
  traversalPath: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
  },
  pathItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nodeValue: {
    fontSize: 16,
    fontWeight: '600',
    padding: 10,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    minWidth: 45,
    textAlign: 'center',
    color: '#6b7280',
  },
  currentNodeValue: {
    backgroundColor: CURRENT_COLOR,
    color: 'white',
  },
  visitedNodeValue: {
    backgroundColor: VISITED_COLOR,
    color: 'white',
  },
  arrow: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#9ca3af',
    marginHorizontal: 8,
  },
  legendCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  legendTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#3b82f6',
    textAlign: 'center',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  legendNode: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#f3f4f6',
    borderWidth: 2,
    borderColor: '#d1d5db',
    marginRight: 12,
  },
  legendCurrent: {
    backgroundColor: CURRENT_COLOR,
    borderColor: '#d97706',
  },
  legendVisited: {
    backgroundColor: VISITED_COLOR,
    borderColor: '#059669',
  },
  treeLineExample: {
    width: 40,
    height: 2,
    backgroundColor: '#94a3b8',
    marginRight: 12,
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  infoCardDFS: {
    backgroundColor: '#f0f9ff',
    borderLeftColor: '#3b82f6',
  },
  infoCardBFS: {
    backgroundColor: '#faf5ff',
    borderLeftColor: '#8b5cf6',
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#3b82f6',
  },
  infoText: {
    fontSize: 14,
    lineHeight: 22,
    color: '#374151',
  },
});