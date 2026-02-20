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

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type TreeNode = {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
  id: string;
};

// Parse input string to numbers array, ignoring empty values and invalid numbers
const parseInputToNumbers = (input: string): number[] => {
  return input
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0) // Remove empty strings
    .map(s => {
      const num = parseInt(s, 10);
      return isNaN(num) ? null : num; // Convert invalid to null
    })
    .filter((num): num is number => num !== null && num > 0) // Keep only valid positive numbers
    .slice(0, 15); // Limit to 15 nodes
};

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

// Inorder traversal
const inorderTraversal = (root: TreeNode | null, result: TreeNode[] = []) => {
  if (!root) return result;
  inorderTraversal(root.left, result);
  result.push(root);
  inorderTraversal(root.right, result);
  return result;
};

// Generate random tree array - maximum 15 nodes
const generateRandomTreeArray = () => {
  const maxNodes = 15;
  const size = Math.floor(Math.random() * (maxNodes - 3)) + 3; // 3 to 15 nodes
  
  const arr: number[] = [];
  for (let i = 0; i < size; i++) {
    arr.push(Math.floor(Math.random() * 100) + 1);
  }
  return arr;
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

// For Web visual tree - Calculate node positions
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

// Tree Node Component for web visual tree
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

// Tree Line Component for web visual tree
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

export function InorderTraversalVisualizer() {
  const [input, setInput] = useState('6,27,21,96,64,64,4,12,19,14,49,1,2,34');
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
  const [parsedNumbers, setParsedNumbers] = useState<number[]>([]);
  const [inputError, setInputError] = useState('');
  const timer = useRef<NodeJS.Timeout | null>(null);
  const animation = useRef(new Animated.Value(0)).current;
  const treeScrollViewRef = useRef<ScrollView>(null);
  const treeContainerRef = useRef<View>(null);

  useEffect(() => {
    const parsed = parseInputToNumbers(input);
    setParsedNumbers(parsed);
    
    if (input.length > 0 && parsed.length === 0) {
      setInputError('Please enter valid positive numbers separated by commas');
      setRoot(null);
      setTotalNodes(0);
      setTreeHeight(0);
      return;
    }
    
    setInputError('');
    
    if (parsed.length === 0) {
      setRoot(null);
      setTotalNodes(0);
      setTreeHeight(0);
      return;
    }
    
    try {
      const tree = buildTree(parsed);
      
      if (tree) {
        setRoot(tree);
        resetTraversal();
        
        const height = getTreeHeight(tree);
        const nodes = getTotalNodes(tree);
        setTreeHeight(height);
        setTotalNodes(nodes);
        
        if (Platform.OS === 'web') {
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
        }
      } else {
        setRoot(null);
        setTotalNodes(0);
        setTreeHeight(0);
      }
    } catch (e) {
      setInputError('Unable to build tree. Please check your input.');
    }
  }, [input, treeContainerWidth]);

  const handleInputChange = (text: string) => {
    setInput(text);
  };

  const handleInputBlur = () => {
    const parsed = parseInputToNumbers(input);
    if (parsed.length > 0) {
      setInput(parsed.join(','));
    } else {
      setInput('');
    }
  };

  const handleTreeContainerLayout = (event: any) => {
    if (Platform.OS === 'web') {
      const { width } = event.nativeEvent.layout;
      const newWidth = Math.max(width, SCREEN_WIDTH * 0.8);
      setTreeContainerWidth(newWidth);
    }
  };

  const startTraversal = () => {
    if (!root || totalNodes === 0) {
      Alert.alert('Invalid Tree', 'Please enter a valid tree with positive numbers only.');
      return;
    }
    const seq = inorderTraversal(root, []);
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

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>🌳 Inorder Traversal Visualizer</Text>
        <Text style={styles.subtitle}>Left → Root → Right</Text>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Tree Input</Text>
          <Text style={styles.inputHint}>
            Enter numbers only (comma-separated, maximum 15 nodes):
          </Text>
          <TextInput
            style={[
              styles.input,
              inputError ? styles.inputError : null
            ]}
            placeholder="e.g. 6,27,21,96,64,64,4,12,19,14,49,1,2,34"
            value={input}
            onChangeText={handleInputChange}
            onBlur={handleInputBlur}
            editable={!isPlaying}
            keyboardType="numbers-and-punctuation"
          />
          
          {root && totalNodes > 0 && (
            <Text style={styles.treeStats}>
              🌳 Tree: {totalNodes} nodes (Max: 15), Height: {treeHeight}
              {Platform.OS === 'web' && ` | 📏 Auto-size: ${Math.round(nodeRadius * 2)}px nodes, ${levelHeight}px spacing`}
            </Text>
          )}
          
          {inputError ? (
            <Text style={styles.errorText}>{inputError}</Text>
          ) : parsedNumbers.length >= 15 ? (
            <Text style={styles.warningText}>
              ⚠️ Maximum 15 nodes allowed. Extra nodes will be ignored.
            </Text>
          ) : null}
          
          {parsedNumbers.length > 0 && (
            <Text style={styles.infoText}>
              ✅ Parsed {parsedNumbers.length} valid nodes: {parsedNumbers.join(', ')}
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
            {currentIdx === -1 ? 'Ready to start inorder traversal' : 
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

        {!root && parsedNumbers.length > 0 && (
          <View style={styles.errorCard}>
            <Text style={styles.errorCardTitle}>⚠️ Tree Construction Error</Text>
            <Text style={styles.errorCardText}>
              Unable to build tree from input. Please check:
              {"\n"}• All values are valid numbers (1-100)
              {"\n"}• Input format: comma-separated numbers
              {"\n"}• Example: 6,27,21,96,64,64,4,12,19,14,49,1,2,34
            </Text>
          </View>
        )}

        {order.length > 0 && (
          <View style={styles.traversalCard}>
            <Text style={styles.traversalTitle}>Inorder Traversal Path:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={Platform.OS !== 'web'}>
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

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Inorder Traversal:</Text>
          <Text style={styles.infoText}>
            • 🌳 Order: Left subtree → Root → Right subtree{'\n'}
            • 🎯 For BST: Produces sorted output in ascending order{'\n'}
            • ⚡ Time Complexity: O(n) where n is number of nodes{'\n'}
            • 💾 Space Complexity: O(h) where h is height of tree{'\n'}
            • 📊 Uses: Expression evaluation, BST operations{'\n'}
            • 🔍 Algorithm: Recursively traverse left, visit root, traverse right{'\n'}
            • ✅ Input: Only positive numbers (1-100), empty/negative/null values ignored{'\n'}
            • 📱 Platform: {Platform.OS === 'web' ? 'Web (Visual View)' : 'Mobile (Text View)'}
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const CURRENT_COLOR = '#f59e0b';
const VISITED_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight || 0,
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
    color: PRIMARY_COLOR,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 24,
    textAlign: 'center',
  },
  inputSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
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
  inputError: {
    borderColor: '#ef4444',
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
  infoText: {
    fontSize: 12,
    color: '#0ea5e9',
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
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 20,
    flexWrap: 'wrap',
  },
  controlButton: {
    flex: 1,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    minWidth: 110,
    maxWidth: Platform.OS === 'web' ? '20%' : undefined,
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
    fontSize: 14,
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
    fontSize: 16,
    fontWeight: '600',
    color: PRIMARY_COLOR,
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
    fontSize: 18,
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
  treeHint: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 12,
    fontStyle: 'italic',
  },
  treeText: {
    fontSize: 16,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : Platform.OS === 'android' ? 'monospace' : 'monospace',
    lineHeight: 24,
    color: '#1f2937',
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
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  traversalPath: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    flexWrap: Platform.OS === 'web' ? 'wrap' : 'nowrap',
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
    color: PRIMARY_COLOR,
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
    borderLeftColor: PRIMARY_COLOR,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
  },
});