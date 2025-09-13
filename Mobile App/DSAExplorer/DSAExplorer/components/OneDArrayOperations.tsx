import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  Alert,
  StatusBar,
  Dimensions,
  TouchableOpacity,
  Modal,
  TextInput,
  ScrollView,
  Platform,
} from 'react-native';

const BOX_SIZE = 60;
const BOX_MARGIN = 8;
const { width } = Dimensions.get('window');
const NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));

type ModalType = 'add' | 'update' | 'search' | null;

export function OneDArrayOperations() {
  const [array, setArray] = useState<number[]>([]);
  const [modalType, setModalType] = useState<ModalType>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [indexValue, setIndexValue] = useState('');
  const [highlightIndex, setHighlightIndex] = useState<number | null>(null);
  const [explanation, setExplanation] = useState('Array is empty. Start by adding elements.');

  const openModal = (type: ModalType) => {
    setModalType(type);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setInputValue('');
    setIndexValue('');
  };

  const handleSubmit = () => {
    const value = parseInt(inputValue);
    const idx = parseInt(indexValue);

    switch (modalType) {
      case 'add':
        // Expecting comma-separated values to add at the end
        if (!inputValue.trim()) {
          return Alert.alert('Invalid input', 'Enter comma-separated values like "1,2,3"');
        }
        const newElements = inputValue
          .split(',')
          .map((v) => parseInt(v.trim()))
          .filter((n) => !isNaN(n));
        if (newElements.length === 0) return Alert.alert('Invalid input', 'No valid numbers entered.');
        setArray([...array, ...newElements]);
        setExplanation(`Added elements: [${newElements.join(', ')}]`);
        break;

      case 'update':
        if (isNaN(idx) || isNaN(value)) {
          return Alert.alert('Invalid input', 'Enter valid index and value.');
        }
        if (idx < 0 || idx >= array.length) {
          return Alert.alert('Out of bounds', 'Index out of range.');
        }
        const updatedArray = array.map((el, i) => (i === idx ? value : el));
        setArray(updatedArray);
        setExplanation(`Updated index ${idx} to ${value}`);
        break;

      case 'search':
        if (isNaN(value)) {
          return Alert.alert('Invalid input', 'Enter a number to search.');
        }
        const foundIndex = array.indexOf(value);
        if (foundIndex !== -1) {
          setHighlightIndex(foundIndex);
          setExplanation(`Found ${value} at index ${foundIndex}`);
          Alert.alert('Found', `Value found at index ${foundIndex}`);
        } else {
          setHighlightIndex(null);
          setExplanation(`${value} not found in array`);
          Alert.alert('Not Found', 'Value not found in array');
        }
        break;
    }

    closeModal();
  };

  const resetArray = () => {
    setArray([]);
    setHighlightIndex(null);
    setExplanation('Array reset. Start adding elements again.');
  };

  const generateRandomArray = () => {
    const randomArray = Array.from({ length: 10 }, () => 
      Math.floor(Math.random() * 20) + 1
    );
    setArray(randomArray);
    setHighlightIndex(null);
    setExplanation(`Generated random array with ${randomArray.length} elements`);
  };

  const renderArray = () => {
    return (
      <View style={styles.row}>
        {array.map((cell, idx) => {
          const isHighlighted = highlightIndex === idx;
          return (
            <View
              key={idx}
              style={[styles.box, isHighlighted && styles.highlightBox]}
            >
              <Text style={[styles.boxText, isHighlighted && { color: 'white' }]}>{cell}</Text>
              <Text style={styles.indexText}>{idx}</Text>
            </View>
          );
        })}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <View style={styles.container}>
          <Text style={styles.header}>🧮 1D Array Operations</Text>
          <Text style={styles.explanation}>{explanation}</Text>

          {/* Operation Buttons */}
          <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.button} onPress={() => openModal('add')}>
            <Text style={styles.buttonText}>Add Elements</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={() => openModal('update')}>
            <Text style={styles.buttonText}>Update Element</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={() => openModal('search')}>
            <Text style={styles.buttonText}>Search Element</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.button, styles.randomButton]} onPress={generateRandomArray}>
            <Text style={styles.buttonText}>Generate Random Array</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.button, styles.resetButton]} onPress={resetArray}>
            <Text style={styles.buttonText}>Reset Array</Text>
          </TouchableOpacity>
          </View>

          {/* Array Display */}
          {array.length > 0 && (
            <View style={styles.arrayContainer}>
              <Text style={styles.arrayTitle}>Array Visualization:</Text>
              {renderArray()}
            </View>
          )}

          {/* Info Card */}
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>ℹ️ Array Information:</Text>
            <Text style={styles.infoText}>
              • Array Length: {array.length}{'\n'}
              • Array Type: 1-dimensional{'\n'}
              • Index Range: 0 to {array.length - 1}{'\n'}
              • Operations: Add, Update, Search
            </Text>
          </View>

          {/* Legend */}
          <View style={styles.legendCard}>
            <Text style={styles.legendTitle}>Legend:</Text>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, styles.highlightBox]} />
              <Text style={styles.legendText}>Found element (search result)</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, styles.box]} />
              <Text style={styles.legendText}>Regular array element</Text>
            </View>
          </View>

          {/* Modal for Input */}
          <Modal visible={modalVisible} animationType="slide" transparent>
            <View style={styles.modalOverlay}>
              <View style={styles.modalContainer}>
                <Text style={styles.modalTitle}>{modalType?.toUpperCase()}</Text>

                {modalType === 'add' ? (
                  <TextInput
                    placeholder='Comma-separated elements (e.g. 1,2,3)'
                    value={inputValue}
                    onChangeText={setInputValue}
                    style={styles.modalInput}
                    keyboardType="default"
                    autoCapitalize="none"
                  />
                ) : (
                  <>
                    {(modalType === 'update') && (
                      <TextInput
                        placeholder="Index"
                        value={indexValue}
                        onChangeText={setIndexValue}
                        keyboardType="numeric"
                        style={styles.modalInput}
                      />
                    )}
                    <TextInput
                      placeholder={modalType === 'search' ? 'Value to search' : 'New Value'}
                      value={inputValue}
                      onChangeText={setInputValue}
                      keyboardType="numeric"
                      style={styles.modalInput}
                    />
                  </>
                )}

                <View style={styles.modalButtonRow}>
                  <TouchableOpacity style={styles.modalButton} onPress={handleSubmit}>
                    <Text style={styles.buttonText}>Submit</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.modalButton, styles.cancelButton]} onPress={closeModal}>
                    <Text style={styles.buttonText}>Cancel</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          </Modal>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const HIGHLIGHT_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight,
  },
  container: {
    flex: 1,
    padding: 24,
    paddingBottom: 100,
  },
  header: {
    fontSize: 28,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
    textAlign: 'center',
  },
  explanation: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 20,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  buttonRow: {
    ...(Platform.OS === "web" && {
      flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    gap: 4,
    }),
    paddingVertical:10
  },
  button: {
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    marginBottom: 12,
    alignItems: 'center',
    ...(Platform.OS === "web" && {
      width: '20%',
    })
  },
  resetButton: {
    backgroundColor: '#ef4444',
  },
  randomButton: {
    backgroundColor: '#8b5cf6',
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
  },
  arrayContainer: {
    marginTop: 24,
    marginBottom: 16,
    alignItems: 'center',
  },
  arrayTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: BOX_MARGIN / 2,
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    backgroundColor: 'white',
    marginHorizontal: BOX_MARGIN / 2,
    marginVertical: BOX_MARGIN / 2,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  highlightBox: {
    backgroundColor: HIGHLIGHT_COLOR,
    borderColor: HIGHLIGHT_COLOR,
  },
  boxText: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  indexText: {
    position: 'absolute',
    top: 4,
    fontSize: 10,
    fontWeight: '600',
    color: '#6b7280',
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 16,
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
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
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

  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    backgroundColor: 'white',
    width: Platform.OS == "web" ? '50%' :'85%',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
  },
  modalInput: {
    width: '100%',
    height: 50,
    borderWidth: 1.5,
    borderColor: '#d1d5db',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
    color: '#1f2937',
    marginBottom: 12,
  },
  modalButtonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  
    width: '50%'
  },
  modalButton: {
    flex: 1,
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 14,
    marginRight: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#6b7280',
    marginRight: 0,
    marginLeft: 8,
  },
});