import React, { useState, useRef } from 'react';
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
  Platform,
} from 'react-native';

let BOX_SIZE: number;
let BOX_MARGIN: number;
let NUM_COLUMNS: number;

if (Platform.OS !== "web") {
  BOX_MARGIN = 5;
  const { width } = Dimensions.get('window');
  NUM_COLUMNS = 5;
  BOX_SIZE = Math.floor((width - (NUM_COLUMNS + 10) * BOX_MARGIN) / NUM_COLUMNS);
} else {
  BOX_SIZE = 80;
  BOX_MARGIN = 4;
  const { width } = Dimensions.get('window');
  NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));
}

const PRIMARY_COLOR = '#2563eb';
const SUCCESS_COLOR = '#10b981';
const CURRENT_COLOR = '#f59e0b';
const LIGHT_BG = '#f9fafb';

export function LinearSearch() {
  const [arrayInput, setArrayInput] = useState('3,5,2,8,4,7,1,9,6');
  const [targetInput, setTargetInput] = useState('4');
  const [speed, setSpeed] = useState(1000);
  const [array, setArray] = useState<number[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number | null>(null);
  const [foundIndex, setFoundIndex] = useState<number | null>(null);
  const [status, setStatus] = useState('Ready to search');
  const [isSearching, setIsSearching] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const parseInputArray = (input: string): number[] => {
    return input
      .split(',')
      .map((item) => parseInt(item.trim()))
      .filter((num) => !isNaN(num));
  };

  const startSearch = () => {
    const parsedArray = parseInputArray(arrayInput);
    const target = parseInt(targetInput.trim());

    if (parsedArray.length === 0 || isNaN(target)) {
      setStatus('⚠️ Please enter valid array and target');
      return;
    }

    setArray(parsedArray);
    setIsSearching(true);
    setFoundIndex(null);
    setCurrentIndex(null);
    setStatus('🔍 Starting linear search...');

    let index = 0;

    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setCurrentIndex(index);
      setStatus(`Checking index ${index}: ${parsedArray[index]}`);

      if (parsedArray[index] === target) {
        setFoundIndex(index);
        setStatus(`🎉 Target ${target} found at index ${index}!`);
        setIsSearching(false);
        if (timerRef.current) clearInterval(timerRef.current);
      } else {
        index++;
        if (index >= parsedArray.length) {
          setStatus(`❌ Target ${target} not found in the array`);
          setIsSearching(false);
          if (timerRef.current) clearInterval(timerRef.current);
          setCurrentIndex(null);
        }
      }
    }, speed);
  };

  const resetSearch = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setIsSearching(false);
    setCurrentIndex(null);
    setFoundIndex(null);
    setStatus('Ready to search');
  };

  const generateRandomArray = () => {
    const randomArray = Array.from({ length: 10 }, () => Math.floor(Math.random() * 20) + 1);
    const randomTarget = randomArray[Math.floor(Math.random() * randomArray.length)];
    setArrayInput(randomArray.join(','));
    setTargetInput(randomTarget.toString());
    resetSearch();
  };

  const changeSpeed = (newSpeed: number) => {
    setSpeed(newSpeed);
    if (isSearching && timerRef.current) {
      resetSearch();
      setTimeout(startSearch, 100);
    }
  };

  const renderItem = ({ item, index }: { item: number; index: number }) => {
    const isCurrent = index === currentIndex;
    const isFound = index === foundIndex;

    return (
      <View
        style={[
          styles.box,
          isFound && styles.foundBox,
          isCurrent && !isFound && styles.currentBox,
        ]}
      >
        <Text style={[styles.boxText, (isFound || isCurrent) && styles.boxTextActive]}>
          {item}
        </Text>
        <Text style={styles.indexText}>{index}</Text>
        {isCurrent && !isFound && <Text style={styles.labelText}>checking</Text>}
        {isFound && <Text style={styles.labelText}>found</Text>}
      </View>
    );
  };

  const getSpeedLabel = (speed: number) => {
    if (speed === 2000) return '🐢 Very Slow';
    if (speed === 1000) return '🚶 Slow';
    if (speed === 500) return '🏃 Medium';
    if (speed === 250) return '⚡ Fast';
    return `${speed}ms`;
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>🔎 Linear Search Visualizer</Text>
        </View>

        <Text style={styles.label}>Enter array (comma-separated numbers):</Text>
        <TextInput
          placeholder="e.g. 3,5,2,8,4,7,1,9,6"
          value={arrayInput}
          onChangeText={setArrayInput}
          style={[styles.input, isSearching && styles.inputDisabled]}
          editable={!isSearching}
          keyboardType="numbers-and-punctuation"
        />

        <Text style={styles.label}>Enter target number:</Text>
        <TextInput
          placeholder="e.g. 4"
          value={targetInput}
          onChangeText={setTargetInput}
          style={[styles.input, isSearching && styles.inputDisabled]}
          editable={!isSearching}
          keyboardType="numeric"
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
                  isSearching && styles.speedBtnDisabled,
                ]}
                onPress={() => changeSpeed(spd)}
                disabled={isSearching}
              >
                <Text style={[styles.speedBtnText, speed === spd && styles.speedBtnTextActive]}>
                  {getSpeedLabel(spd)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.actionSection}>
          <TouchableOpacity
            style={[styles.actionBtn, styles.startBtn, isSearching && styles.btnDisabled]}
            onPress={startSearch}
            disabled={isSearching}
          >
            <Text style={styles.btnText}>▶️ Start Search</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.actionBtn, styles.resetBtn]} onPress={resetSearch}>
            <Text style={styles.btnText}>🔄 Reset</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionBtn, styles.randomBtn, isSearching && styles.btnDisabled]}
            onPress={generateRandomArray}
            disabled={isSearching}
          >
            <Text style={styles.btnText}>🎲 Random</Text>
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
          <Text style={styles.infoTitle}>📖 About Linear Search:</Text>
          <Text style={styles.infoText}>
            • 🔍 Checks each element sequentially from start to end{'\n'}
            • ⏱️ Time Complexity: O(n) - linear time{'\n'}
            • 💾 Space Complexity: O(1) - constant space{'\n'}
            • 🎯 Simple but effective for small arrays{'\n'}
            • 📊 Works on both sorted and unsorted arrays
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.currentBox]} />
            <Text style={styles.legendText}>Current element being checked</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.foundBox]} />
            <Text style={styles.legendText}>Target element found</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.box]} />
            <Text style={styles.legendText}>Not yet checked</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: LIGHT_BG },
  scrollView: { flex: 1 },
  scrollContent: { paddingHorizontal: 16, paddingBottom: 40 },
  header: {
    alignItems: 'center',
    marginVertical: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: PRIMARY_COLOR,
    textAlign: 'center',
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
    justifyContent: 'center',
    gap: 8,
  },
  speedBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 2,
    borderColor: 'transparent',
    minWidth: 30,
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
    gap: 8,
    justifyContent: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
  },
  actionBtn: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 110,
  },
  startBtn: { backgroundColor: PRIMARY_COLOR },
  resetBtn: { backgroundColor: '#6b7280' },
  randomBtn: { backgroundColor: '#8b5cf6' },
  btnDisabled: { opacity: 0.5 },
  btnText: { color: 'white', fontWeight: '700', fontSize: 14 },
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
    padding: 16,
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
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    backgroundColor: 'white',
    margin: BOX_MARGIN,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  foundBox: {
    backgroundColor: SUCCESS_COLOR,
    borderColor: SUCCESS_COLOR,
  },
  currentBox: {
    backgroundColor: CURRENT_COLOR,
    borderColor: CURRENT_COLOR,
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