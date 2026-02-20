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
  val: number | string;
  left: TreeNode | null;
  right: TreeNode | null;
  id: string;
  x?: number;
  y?: number;
};

// Build tree from level-order array using iterative approach
const buildTree = (arr: (number | string | null)[]): TreeNode | null => {
  if (arr.length === 0 || arr[0] === null) return null;
  
  // Create root node
  const root: TreeNode = {
    val: arr[0] as number | string,
    left: null,
    right: null,
    id: Math.random().toString(36).substr(2, 9),
  };
  
  // Use a queue to build the tree level by level
  const queue: Array<{ node: TreeNode; index: number }> = [];
  queue.push({ node: root, index: 0 });
  
  while (queue.length > 0) {
    const { node, index } = queue.shift()!;
    
    // Calculate indices for left and right children
    const leftIndex = 2 * index + 1;
    const rightIndex = 2 * index + 2;
    
    // Create left child if it exists and is not null
    if (leftIndex < arr.length && arr[leftIndex] !== null) {
      node.left = {
        val: arr[leftIndex] as number | string,
        left: null,
        right: null,
        id: Math.random().toString(36).substr(2, 9),
      };
      queue.push({ node: node.left, index: leftIndex });
    }
    
    // Create right child if it exists and is not null
    if (rightIndex < arr.length && arr[rightIndex] !== null) {
      node.right = {
        val: arr[rightIndex] as number | string,
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

// Calculate node positions for graphical tree view (used on web/desktop)
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
  
  // Dynamic sizing based on tree size
  let baseNodeRadius = Platform.OS === 'web' ? 25 : 30;
  let baseLevelHeight = Platform.OS === 'web' ? 50 : 60;
  
  // Adjust for larger trees
  if (totalNodes > 10) {
    baseNodeRadius = Math.max(18, baseNodeRadius - (totalNodes - 10) * 0.5);
    baseLevelHeight = Math.max(35, baseLevelHeight - (totalNodes - 10) * 1.5);
  }
  
  // Adjust for taller trees
  if (treeHeight > 5) {
    baseLevelHeight = Math.max(30, baseLevelHeight - (treeHeight - 5) * 2);
    baseNodeRadius = Math.max(15, baseNodeRadius - (treeHeight - 5) * 0.7);
  }
  
  const nodeRadius = baseNodeRadius;
  const levelHeight = baseLevelHeight;
  const nodeDiameter = nodeRadius * 2;
  
  // Calculate positions using BFS with improved spacing
  const queue: Array<{ node: TreeNode; level: number; minX: number; maxX: number }> = [];
  
  // Start with root at center
  queue.push({ 
    node: root, 
    level: 0, 
    minX: 0, 
    maxX: containerWidth 
  });

  while (queue.length > 0) {
    const { node, level, minX, maxX } = queue.shift()!;
    
    // Calculate x position at center of available space
    const x = (minX + maxX) / 2;
    const y = level * levelHeight + nodeRadius + 20;
    
    // Ensure node stays within bounds with margin
    const margin = nodeRadius + 5;
    const boundedX = Math.max(margin, Math.min(containerWidth - margin, x));
    
    positions.set(node.id, { x: boundedX, y });

    // Calculate positions for children
    if (node.left || node.right) {
      const availableWidth = maxX - minX;
      
      // Dynamic spacing based on tree level and available width
      const spacingFactor = Math.min(0.45, 0.65 / (level + 1));
      const spacing = availableWidth * spacingFactor;
      
      if (node.left) {
        const leftMaxX = boundedX - spacing / 2;
        if (leftMaxX > minX + nodeDiameter) {
          queue.push({ 
            node: node.left, 
            level: level + 1, 
            minX, 
            maxX: leftMaxX 
          });
        } else {
          queue.push({ 
            node: node.left, 
            level: level + 1, 
            minX: minX + nodeDiameter,
            maxX: boundedX - nodeDiameter
          });
        }
      }
      
      if (node.right) {
        const rightMinX = boundedX + spacing / 2;
        if (rightMinX < maxX - nodeDiameter) {
          queue.push({ 
            node: node.right, 
            level: level + 1, 
            minX: rightMinX, 
            maxX 
          });
        } else {
          queue.push({ 
            node: node.right, 
            level: level + 1, 
            minX: boundedX + nodeDiameter,
            maxX: maxX - nodeDiameter
          });
        }
      }
    }
  }

  return { positions, nodeRadius, levelHeight };
};

// Postorder traversal collecting nodes
const postorderTraversal = (root: TreeNode | null, result: TreeNode[] = []) => {
  if (!root) return result;
  postorderTraversal(root.left, result);
  postorderTraversal(root.right, result);
  result.push(root);
  return result;
};

// Generate random tree array - maximum 15 nodes
const generateRandomTreeArray = () => {
  const maxNodes = Platform.OS === 'web' ? 20 : 15;
  const size = Math.floor(Math.random() * (maxNodes - 3)) + 3;
  
  const arr: (number | null)[] = [];
  for (let i = 0; i < size; i++) {
    // Randomly include some null nodes for more interesting trees
    const includeNull = Math.random() > 0.7 && i > 0;
    if (includeNull) {
      arr.push(null);
    } else {
      arr.push(Math.floor(Math.random() * 100) + 1);
    }
  }
  // Ensure root is never null
  if (arr[0] === null) arr[0] = Math.floor(Math.random() * 100) + 1;
  return arr;
};

// Parse input string to array
const parseInputToArray = (input: string): (number | string | null)[] => {
  return input
    .split(',')
    .map(s => s.trim())
    .map(s => {
      if (s.toLowerCase() === 'null') return null;
      const num = parseInt(s, 10);
      return isNaN(num) ? s : num;
    });
};

// Tree Node Component for graphical view
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

// Tree Line Component for graphical view
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

// Render tree as text with proper indentation (for Android/mobile)
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

// Get edges for tree lines
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

export function PostorderTraversalVisualizer() {
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
  const [useGraphicalView, setUseGraphicalView] = useState(Platform.OS === 'web');
  
  const timer = useRef<NodeJS.Timeout | null>(null);
  const animation = useRef(new Animated.Value(0)).current;
  const treeScrollViewRef = useRef<ScrollView>(null);
  const treeContainerRef = useRef<View>(null);

  useEffect(() => {
    try {
      const arr = parseInputToArray(input);
      
      if (arr.length === 0 || arr[0] === null) {
        setRoot(null);
        setTotalNodes(0);
        setTreeHeight(0);
        return;
      }
      
      const tree = buildTree(arr);
      
      if (tree) {
        setRoot(tree);
        resetTraversal();
        
        const height = getTreeHeight(tree);
        const nodes = getTotalNodes(tree);
        setTreeHeight(height);
        setTotalNodes(nodes);
        
        // Only calculate positions for graphical view
        if (useGraphicalView) {
          const { positions, nodeRadius: radius, levelHeight: lHeight } = 
            calculateNodePositions(tree, treeContainerWidth);
          setNodePositions(positions);
          setNodeRadius(radius);
          setLevelHeight(lHeight);
        }
      } else {
        setRoot(null);
        setTotalNodes(0);
        setTreeHeight(0);
      }
    } catch (e) {
      Alert.alert('Error', 'Invalid tree input format');
    }
  }, [input, treeContainerWidth, useGraphicalView]);

  const handleInputChange = (text: string) => {
    setInput(text);
  };

  const startTraversal = () => {
    if (!root || totalNodes === 0) {
      Alert.alert('Invalid Tree', 'Please enter a valid tree with numbers only.');
      return;
    }
    const seq = postorderTraversal(root, []);
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
    setInput(arr.map(v => v === null ? 'null' : v.toString()).join(','));
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

  const handleTreeContainerLayout = (event: any) => {
    const { width } = event.nativeEvent.layout;
    const newWidth = Math.max(width, SCREEN_WIDTH * 0.8);
    setTreeContainerWidth(newWidth);
  };

  const renderGraphicalTree = () => {
    if (!root) return null;
    const edges = getTreeEdges(root);
    
    const getTreeVisualizationHeight = () => {
      const minHeight = 200;
      const maxHeight = Platform.OS === 'web' ? 500 : 450;
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

    return (
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
            {edges.map(([parentId, childId], index) => (
              <TreeLineComponent
                key={`${parentId}-${childId}`}
                startId={parentId}
                endId={childId}
                positions={nodePositions}
                lineWidth={Math.max(1, 3 - treeHeight * 0.2)}
              />
            ))}
            {renderTreeNodes(root)}
          </View>
        </ScrollView>
      </View>
    );
  };

  const renderTextTree = () => {
    return (
      <View style={styles.textTreeContainer}>
        <Text style={styles.treeText}>
          {renderTreeText(root, order, currentIdx)}
        </Text>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>🌿 Postorder Traversal Visualizer</Text>
        <Text style={styles.subtitle}>Left → Right → Root</Text>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Tree Input</Text>
          <Text style={styles.inputHint}>
            Enter level-order values (comma-separated, use "null" for empty nodes):
          </Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. 1,2,3,4,5,null,7"
            value={input}
            onChangeText={handleInputChange}
            editable={!isPlaying}
            keyboardType="numbers-and-punctuation"
          />
          {root && totalNodes > 0 && (
            <Text style={styles.treeStats}>
              🌿 Tree: {totalNodes} nodes, Height: {treeHeight} | 
              {useGraphicalView ? ` 📏 Auto-size: ${Math.round(nodeRadius * 2)}px nodes` : ' 📱 Text View'}
            </Text>
          )}
          {parseInputToArray(input).length >= (Platform.OS === 'web' ? 20 : 15) && (
            <Text style={styles.warningText}>
              ⚠️ Maximum {Platform.OS === 'web' ? '20' : '15'} nodes recommended. Performance may be affected.
            </Text>
          )}
        </View>

        {Platform.OS === 'web' && (
          <View style={styles.viewToggleSection}>
            <Text style={styles.viewToggleLabel}>View Mode:</Text>
            <View style={styles.viewToggleButtons}>
              <TouchableOpacity
                style={[
                  styles.viewToggleBtn,
                  useGraphicalView && styles.viewToggleBtnActive,
                  isPlaying && styles.viewToggleBtnDisabled
                ]}
                onPress={() => setUseGraphicalView(true)}
                disabled={isPlaying}
              >
                <Text style={[
                  styles.viewToggleBtnText,
                  useGraphicalView && styles.viewToggleBtnTextActive
                ]}>
                  🎨 Graphical View
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.viewToggleBtn,
                  !useGraphicalView && styles.viewToggleBtnActive,
                  isPlaying && styles.viewToggleBtnDisabled
                ]}
                onPress={() => setUseGraphicalView(false)}
                disabled={isPlaying}
              >
                <Text style={[
                  styles.viewToggleBtnText,
                  !useGraphicalView && styles.viewToggleBtnTextActive
                ]}>
                  📱 Text View
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

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
            <Text style={styles.buttonText}>▶️ Start Traversal</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.resetButton, !isPlaying && currentIdx === -1 && styles.buttonDisabled]}
            onPress={resetTraversal}
            disabled={!isPlaying && currentIdx === -1}
          >
            <Text style={styles.buttonText}>🔄 Reset</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.randomButton]}
            onPress={generateRandomTree}
            disabled={isPlaying}
          >
            <Text style={styles.buttonText}>🎲 Random Tree</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.status}>
            {currentIdx === -1 ? 'Ready to start postorder traversal' : 
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

        {root && totalNodes > 0 && (
          <View style={styles.treeCard}>
            <Text style={styles.treeTitle}>Binary Tree Visualization:</Text>
            {useGraphicalView ? renderGraphicalTree() : renderTextTree()}
            <Text style={styles.treeHint}>
              {useGraphicalView ? 
                '💡 Tip: Scroll horizontally to view the entire tree. Tap on nodes for details.' :
                '💡 Tip: 🟡 = Current node, ✅ = Visited nodes'
              }
            </Text>
          </View>
        )}

        {order.length > 0 && (
          <View style={styles.traversalCard}>
            <Text style={styles.traversalTitle}>Postorder Traversal Path:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={Platform.OS === 'web'}>
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
            <Text style={styles.legendEmoji}>🟡</Text>
            <Text style={styles.legendText}>Current node being visited</Text>
          </View>
          <View style={styles.legendItem}>
            <Text style={styles.legendEmoji}>✅</Text>
            <Text style={styles.legendText}>Already visited nodes</Text>
          </View>
          <View style={styles.legendItem}>
            <Text style={styles.legendEmoji}>→</Text>
            <Text style={styles.legendText}>Traversal direction</Text>
          </View>
          {useGraphicalView && (
            <View style={styles.legendItem}>
              <View style={styles.treeLineExample} />
              <Text style={styles.legendText}>Parent-child connection</Text>
            </View>
          )}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Postorder Traversal:</Text>
          <Text style={styles.infoText}>
            • 🌿 Order: Left subtree → Right subtree → Root{'\n'}
            • 🎯 Useful for deleting trees and expression evaluation{'\n'}
            • ⚡ Time Complexity: O(n) where n is number of nodes{'\n'}
            • 💾 Space Complexity: O(h) where h is height of tree{'\n'}
            • 📊 Uses: Tree deletion, postfix expression evaluation{'\n'}
            • 🔍 Algorithm: Recursively traverse left, traverse right, visit root{'\n'}
            • 📱 Platform: {Platform.OS === 'web' ? 'Web/Desktop' : 'Mobile'} optimized
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const CURRENT_COLOR = '#f59e0b';
const VISITED_COLOR = '#3b82f6';
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
    fontSize: Platform.OS === 'web' ? 32 : 28,
    fontWeight: '800',
    color: PRIMARY_COLOR,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: Platform.OS === 'web' ? 18 : 16,
    color: '#6b7280',
    marginBottom: 24,
    textAlign: 'center',
  },
  inputSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: Platform.OS === 'web' ? 20 : 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 10,
  },
  inputHint: {
    fontSize: Platform.OS === 'web' ? 15 : 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  input: {
    height: Platform.OS === 'web' ? 55 : 50,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: Platform.OS === 'web' ? 17 : 16,
    backgroundColor: 'white',
    color: '#1f2937',
  },
  treeStats: {
    fontSize: 12,
    color: '#2563eb',
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
  viewToggleSection: {
    marginBottom: 20,
  },
  viewToggleLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
  },
  viewToggleButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'center',
  },
  viewToggleBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 1,
    borderColor: 'transparent',
    flex: 1,
    minWidth: 120,
    alignItems: 'center',
  },
  viewToggleBtnActive: {
    backgroundColor: PRIMARY_COLOR,
    borderColor: PRIMARY_COLOR,
  },
  viewToggleBtnDisabled: {
    opacity: 0.6,
  },
  viewToggleBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  viewToggleBtnTextActive: {
    color: 'white',
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
    backgroundColor: PRIMARY_COLOR,
    borderColor: PRIMARY_COLOR,
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
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    gap: 12,
    marginBottom: 20,
  },
  controlButton: {
    borderRadius: 12,
    paddingVertical: Platform.OS === 'web' ? 16 : 14,
    alignItems: 'center',
    ...(Platform.OS === 'web' && {
      flex: 1,
      minWidth: 120,
    }),
  },
  startButton: {
    backgroundColor: PRIMARY_COLOR,
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
    fontSize: Platform.OS === 'web' ? 15 : 14,
  },
  statusContainer: {
    backgroundColor: '#e0e7ff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  status: {
    fontSize: Platform.OS === 'web' ? 17 : 16,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    textAlign: 'center',
    marginBottom: 8,
  },
  progress: {
    fontSize: 14,
    color: '#2563eb',
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
    backgroundColor: PRIMARY_COLOR,
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
    fontSize: Platform.OS === 'web' ? 20 : 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
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
  textTreeContainer: {
    backgroundColor: '#f8fafc',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  treeText: {
    fontSize: Platform.OS === 'web' ? 15 : 14,
    fontFamily: Platform.OS === 'web' ? 'monospace, Menlo, Monaco, Consolas' : 'monospace',
    lineHeight: 24,
    color: '#1f2937',
  },
  treeHint: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 12,
    fontStyle: 'italic',
  },
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
    borderColor: '#1d4ed8',
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
    fontSize: Platform.OS === 'web' ? 20 : 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
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
    fontSize: Platform.OS === 'web' ? 17 : 16,
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
    fontSize: Platform.OS === 'web' ? 20 : 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  legendEmoji: {
    fontSize: 18,
    marginRight: 12,
    width: 28,
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
    borderLeftColor: PRIMARY_COLOR,
  },
  infoTitle: {
    fontSize: Platform.OS === 'web' ? 20 : 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
  },
  infoText: {
    fontSize: Platform.OS === 'web' ? 15 : 14,
    lineHeight: 22,
    color: '#374151',
  },
});