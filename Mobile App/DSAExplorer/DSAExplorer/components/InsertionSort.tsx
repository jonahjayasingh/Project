import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  StyleSheet,
  SafeAreaView,
  FlatList,
  Dimensions,
  ScrollView,
  StatusBar,
  Platform
} from 'react-native';

let BOX_SIZE: number;
let BOX_MARGIN: number;
let NUM_COLUMNS: number;

if (Platform.OS !== "web") {
  BOX_MARGIN = 5;
  const { width } = Dimensions.get('window');
  NUM_COLUMNS = 5;  

  // Adjust box size so 5 boxes + margins fit exactly in screen width
  BOX_SIZE = Math.floor((width - (NUM_COLUMNS + 10) * BOX_MARGIN) / NUM_COLUMNS);
} else{
  BOX_SIZE = 80;
  BOX_MARGIN = 4;
  const { width } = Dimensions.get('window');
  NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));
}

export function InsertionSort() {
  const [arrayInput, setArrayInput] = useState('5,3,8,4,2,7,1,6');
  const [array, setArray] = useState<number[]>([]);
  const [currentIndices, setCurrentIndices] = useState<{ i: number; j: number } | null>(null);
  const [swappingIndices, setSwappingIndices] = useState<{ first: number; second: number } | null>(null);
  const [isSorting, setIsSorting] = useState(false);
  const [status, setStatus] = useState('Ready to sort');
  const [sorted, setSorted] = useState(false);
  const [speed, setSpeed] = useState(1000);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const parseInputArray = (input: string): number[] => {
    return input
      .split(',')
      .map((item) => parseInt(item.trim()))
      .filter((num) => !isNaN(num));
  };

  const startSort = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    const parsedArray = parseInputArray(arrayInput);
    if (parsedArray.length === 0) {
      setStatus('⚠️ Please enter a valid array.');
      return;
    }

    setArray(parsedArray);
    setIsSorting(true);
    setSorted(false);
    setStatus('🔍 Starting insertion sort...');
    setSwappingIndices(null);

    let arr = [...parsedArray];
    let i = 1;
    let j = i;
    let isSwapping = false;

    intervalRef.current = setInterval(() => {
      if (isSwapping) {
        // Reset swapping state after the swap is complete
        setSwappingIndices(null);
        isSwapping = false;
        return;
      }

      if (i < arr.length) {
        if (j > 0 && arr[j - 1] > arr[j]) {
          // Show swapping state
          setSwappingIndices({ first: j, second: j - 1 });
          setStatus(`Swapping ${arr[j]} and ${arr[j - 1]}`);
          isSwapping = true;
          
          // Swap elements in the array
          [arr[j], arr[j - 1]] = [arr[j - 1], arr[j]];
          setArray([...arr]);
          j--;
        } else {
          i++;
          j = i;
        }
        setCurrentIndices({ i, j });
      } else {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setCurrentIndices(null);
        setIsSorting(false);
        setSorted(true);
        setStatus('🎉 Array sorted!');
      }
    }, speed);
  };

  const resetSort = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setIsSorting(false);
    setCurrentIndices(null);
    setSwappingIndices(null);
    setSorted(false);
    setStatus('Ready to sort');
  };

  const generateRandomArray = () => {
    const randomArray = Array.from({ length: 8 }, () => 
      Math.floor(Math.random() * 20) + 1
    );
    
    setArrayInput(randomArray.join(','));
    resetSort();
  };

  const changeSpeed = (newSpeed: number) => {
    setSpeed(newSpeed);
    if (isSorting && intervalRef.current) {
      resetSort();
      setTimeout(startSort, 100);
    }
  };

  const saveBookmark = () => {
    if (!arrayInput) {
      Alert.alert('Cannot bookmark', 'Please enter array first.');
      return;
    }
    Alert.alert(
      'Bookmark Saved',
      `Array: [${arrayInput}]\nSpeed: ${speed} ms`,
      [{ text: 'OK' }]
    );
  };

  const getSpeedLabel = (speed: number) => {
    if (speed === 2000) return '🐢 Very Slow';
    if (speed === 1000) return '🚶 Slow';
    if (speed === 500) return '🏃 Medium';
    if (speed === 250) return '⚡ Fast';
    return `${speed}ms`;
  };

  const renderItem = ({ item, index }: { item: number; index: number }) => {
    const isI = currentIndices !== null && index === currentIndices.i;
    const isJ = currentIndices !== null && index === currentIndices.j;
    const isSwapping = swappingIndices !== null && 
                      (index === swappingIndices.first || index === swappingIndices.second);
    const isSorted = sorted || (currentIndices !== null && index < currentIndices.i);

    return (
      <View
        style={[
          styles.box,
          isI && !isSwapping && styles.currentBox,
          isJ && !isSwapping && styles.compareBox,
          isSwapping && styles.swappingBox,
          isSorted && !isSwapping && styles.sortedBox,
        ]}
      >
        <Text
          style={[
            styles.boxText,
            (isI || isJ || isSwapping || isSorted) && styles.boxTextActive,
          ]}
        >
          {item}
        </Text>
        <Text style={styles.indexText}>{index}</Text>
        {isI && !isSwapping && <Text style={styles.labelText}>i</Text>}
        {isJ && !isI && !isSwapping && <Text style={styles.labelText}>j</Text>}
        {isSwapping && <Text style={styles.labelText}>swapping</Text>}
        {isSorted && !isSwapping && <Text style={styles.labelText}>sorted</Text>}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>📥 Insertion Sort Visualizer</Text>

        <Text style={styles.label}>Enter array (comma-separated numbers):</Text>
        <TextInput
          placeholder="e.g. 5,3,8,4,2,7,1,6"
          value={arrayInput}
          onChangeText={setArrayInput}
          style={[styles.input, isSorting && styles.inputDisabled]}
          editable={!isSorting}
          keyboardType="numbers-and-punctuation"
        />

        <View style={styles.speedSection}>
          <Text style={styles.speedLabel}>Animation Speed:</Text>
          <View style={styles.speedButtons}>
            {[250, 500, 1000, 2000].map((spd) => (
              <TouchableOpacity
                key={spd}
                style={[
                  styles.speedBtn,
                  speed === spd && styles.speedBtnActive,
                  isSorting && styles.speedBtnDisabled
                ]}
                onPress={() => changeSpeed(spd)}
                disabled={isSorting}
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

        <View style={styles.actionSection}>
          <TouchableOpacity 
            style={[styles.actionBtn, styles.startBtn, isSorting && styles.btnDisabled]} 
            onPress={startSort}
            disabled={isSorting}
          >
            <Text style={styles.btnText}>▶️ Start Sort</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionBtn, styles.resetBtn]} 
            onPress={resetSort}
          >
            <Text style={styles.btnText}>🔄 Reset</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionBtn, styles.randomBtn, isSorting && styles.btnDisabled]} 
            onPress={generateRandomArray}
            disabled={isSorting}
          >
            <Text style={styles.btnText}>🎲 Random</Text>
          </TouchableOpacity>
          <TouchableOpacity
          style={[styles.actionBtn, styles.bookmarkButton, isSorting && styles.btnDisabled]}
          onPress={saveBookmark}
          disabled={isSorting}
        >
          <Text style={styles.bookmarkText}>🔖 Bookmark</Text>
        </TouchableOpacity>
        </View>

        

        <View style={styles.statusCard}>
          <Text style={styles.statusText}>{status}</Text>
        </View>

        {array.length > 0 && (
          <View style={styles.arrayContainer}>
            <Text style={styles.arrayTitle}>Array Visualization:</Text>
            <FlatList
              data={array}
              renderItem={renderItem}
              keyExtractor={(_, idx) => idx.toString()}
              numColumns={NUM_COLUMNS}
              scrollEnabled={false}
              contentContainerStyle={styles.flatListContent}
            />
          </View>
        )}

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Insertion Sort:</Text>
          <Text style={styles.infoText}>
            • 📥 Simple sorting algorithm that builds the final sorted array one item at a time{'\n'}
            • ⏱️ Time Complexity: O(n²) - quadratic time{'\n'}
            • 💾 Space Complexity: O(1) - constant space{'\n'}
            • 🎯 Efficient for small data sets or nearly sorted arrays{'\n'}
            • 📊 Works by repeatedly inserting elements into their correct position
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.currentBox]} />
            <Text style={styles.legendText}>Current i pointer</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.compareBox]} />
            <Text style={styles.legendText}>Current j pointer (comparing)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.swappingBox]} />
            <Text style={styles.legendText}>Elements being swapped</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.sortedBox]} />
            <Text style={styles.legendText}>Sorted elements</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.box]} />
            <Text style={styles.legendText}>Unsorted elements</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const SUCCESS_COLOR = '#10b981';
const CURRENT_COLOR = '#f59e0b';
const COMPARE_COLOR = '#8b5cf6';
const SWAPPING_COLOR = '#ef4444';
const SORTED_COLOR = '#6b7280';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    
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
    textAlign: 'center',
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#374151',
  },
  input: {
    height: 50,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
    marginBottom: 16,
    color: '#1f2937',
  },
  inputDisabled: {
    backgroundColor: '#f3f4f6',
    color: '#6b7280',
  },
  speedSection: {
    marginBottom: 16,
  },
  speedLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#374151',
  },
  speedButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'center',
  },
  speedBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 2,
    borderColor: 'transparent',
    minWidth: 100,
    alignItems: 'center',
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
  actionSection: {
    flexDirection: 'row',
    gap: 5,
    justifyContent: 'center',
    marginBottom: 16,
    flexWrap:'wrap'
  },
  actionBtn: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 110,
    marginHorizontal:4,
    marginVertical:4
  },
  startBtn: {
    backgroundColor: PRIMARY_COLOR,
  },
  resetBtn: {
    backgroundColor: '#6b7280',
  },
  randomBtn: {
    backgroundColor: '#8b5cf6',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  bookmarkButton: {
    backgroundColor: '#f59e0b',
  },
  bookmarkText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  statusCard: {
    backgroundColor: '#dbeafe',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e40af',
    textAlign: 'center',
  },
  arrayContainer: {
    backgroundColor: 'white',
    padding: 0,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    alignItems: 'center',
  },
  arrayTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  flatListContent: {
       justifyContent: 'center',
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    margin: 15,
    paddingVertical: 15,
    paddingHorizontal: 10,
    
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    backgroundColor: 'white',
    margin: BOX_MARGIN / 2,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  currentBox: {
    backgroundColor: CURRENT_COLOR,
    borderColor: CURRENT_COLOR,
  },
  compareBox: {
    backgroundColor: COMPARE_COLOR,
    borderColor: COMPARE_COLOR,
  },
  swappingBox: {
    backgroundColor: SWAPPING_COLOR,
    borderColor: SWAPPING_COLOR,
  },
  sortedBox: {
    backgroundColor: SORTED_COLOR,
    borderColor: SORTED_COLOR,
  },
  boxText: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  boxTextActive: {
    color: 'white',
  },
  indexText: {
    position: 'absolute',
    top: 4,
    fontSize: 10,
    fontWeight: '600',
    color: '#6b7280',
  },
  labelText: {
    position: 'absolute',
    bottom: 4,
    fontSize: 10,
    fontWeight: '600',
    color: 'white',
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 4,
    borderRadius: 4,
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
  legendCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
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
  },
  legendColor: {
    width: 20,
    height: 20,
    borderRadius: 6,
    marginRight: 12,
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
});