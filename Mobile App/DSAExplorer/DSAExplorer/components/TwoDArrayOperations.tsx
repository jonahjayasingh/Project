import React, { useState, useEffect } from 'react';
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
import { FontAwesome } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BOX_SIZE = 60;
const BOX_MARGIN = 8;
const { width } = Dimensions.get('window');
const NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));

type ModalType = 'addRow' | 'updateCell' | 'addColumn' | null;

export function TwoDArrayOperations({ navigation }: any) {
  const [matrix, setMatrix] = useState<number[][]>([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
  ]);
  const [modalType, setModalType] = useState<ModalType>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [rowIndex, setRowIndex] = useState('');
  const [colIndex, setColIndex] = useState('');
  const [explanation, setExplanation] = useState('3x3 matrix loaded. You can modify it using the operations below.');
  const [username, setUsername] = useState('');
  const [bookmarks, setBookmarks] = useState<any[]>([]);
  const [showBookmarks, setShowBookmarks] = useState(false);

  useEffect(() => {
    checkUserAuthentication();
    loadBookmarks();
  }, []);

  const checkUserAuthentication = async () => {
    try {
      const user = await AsyncStorage.getItem('currentUser');
      if (!user) {
        // If no user found, navigate back to home
        Alert.alert('Authentication Required', 'Please login to access this feature');
        navigation.goBack();
        return;
      }
      
      const userData = JSON.parse(user);
      setUsername(userData.username);
      setExplanation(`Welcome ${userData.username}! 3x3 matrix loaded.`);
    } catch (error) {
      console.error('Auth check error:', error);
      Alert.alert('Error', 'Failed to verify authentication');
      navigation.goBack();
    }
  };

  const loadBookmarks = async () => {
    try {
      const localBookmarks = await AsyncStorage.getItem('matrixBookmarks');
      if (localBookmarks) {
        setBookmarks(JSON.parse(localBookmarks));
      }
    } catch (error) {
      console.error('Error loading bookmarks:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('currentUser');
      navigation.goBack();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const saveBookmark = async () => {
    if (matrix.length === 0) {
      Alert.alert('Cannot bookmark', 'Matrix is empty');
      return;
    }

    try {
      const newBookmark = {
        id: Date.now(),
        matrix: JSON.parse(JSON.stringify(matrix)),
        date: new Date().toLocaleString(),
        username,
      };

      const updatedBookmarks = [...bookmarks, newBookmark];
      setBookmarks(updatedBookmarks);
      
      await AsyncStorage.setItem('matrixBookmarks', JSON.stringify(updatedBookmarks));
      
      setExplanation(`Bookmark saved!`);
      Alert.alert('Bookmark Saved', 'Matrix state has been bookmarked.');
    } catch (error) {
      console.error('Save bookmark error:', error);
      Alert.alert('Error', 'Failed to save bookmark');
    }
  };

  const loadBookmark = (bookmark: any) => {
    setMatrix(bookmark.matrix);
    setExplanation(`Loaded bookmark from ${bookmark.date}`);
    setShowBookmarks(false);
  };

  const deleteBookmark = async (bookmarkId: number) => {
    try {
      const updatedBookmarks = bookmarks.filter(b => b.id !== bookmarkId);
      setBookmarks(updatedBookmarks);
      
      await AsyncStorage.setItem('matrixBookmarks', JSON.stringify(updatedBookmarks));
      
      setExplanation(`Bookmark deleted`);
    } catch (error) {
      console.error('Delete bookmark error:', error);
      Alert.alert('Error', 'Failed to delete bookmark');
    }
  };

  const renderBookmarksPanel = () => {
    if (!showBookmarks) return null;

    return (
      <View style={styles.bookmarksPanel}>
        <Text style={styles.bookmarksTitle}>Matrix Bookmarks</Text>
        <ScrollView style={styles.bookmarksList}>
          {bookmarks.length === 0 ? (
            <Text style={styles.noBookmarks}>No bookmarks yet</Text>
          ) : (
            bookmarks.map((bookmark, index) => (
              <View key={bookmark.id} style={styles.bookmarkItem}>
                <TouchableOpacity 
                  style={styles.bookmarkContent} 
                  onPress={() => loadBookmark(bookmark)}
                >
                  <Text style={styles.bookmarkIndex}>{index + 1}.</Text>
                  <Text style={styles.bookmarkMatrix}>
                    {bookmark.matrix.length}x{bookmark.matrix[0]?.length || 0} - {bookmark.date}
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={styles.deleteBookmark} 
                  onPress={() => deleteBookmark(bookmark.id)}
                >
                  <FontAwesome name="trash" size={16} color="#ef4444" />
                </TouchableOpacity>
              </View>
            ))
          )}
        </ScrollView>
      </View>
    );
  };

  const openModal = (type: ModalType) => {
    setModalType(type);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setInputValue('');
    setRowIndex('');
    setColIndex('');
  };

  const handleSubmit = () => {
    const value = parseInt(inputValue);
    const row = parseInt(rowIndex);
    const col = parseInt(colIndex);

    switch (modalType) {
      case 'addRow':
        if (!inputValue.trim()) {
          return Alert.alert('Invalid input', 'Enter comma-separated values like "1,2,3"');
        }
        const newRow = inputValue
          .split(',')
          .map((v) => parseInt(v.trim()))
          .filter((n) => !isNaN(n));
        
        if (newRow.length === 0) return Alert.alert('Invalid input', 'No valid numbers entered.');
        
        if (matrix.length > 0 && matrix[0].length !== newRow.length) {
          return Alert.alert('Dimension mismatch', `New row must have ${matrix[0].length} columns`);
        }
        
        setMatrix([...matrix, newRow]);
        setExplanation(`Added new row: [${newRow.join(', ')}]`);
        break;

      case 'addColumn':
        if (isNaN(value)) return Alert.alert('Invalid input', 'Enter a value for the new column.');
        
        const columnMatrix = matrix.map(row => [...row, value]);
        setMatrix(columnMatrix);
        setExplanation(`Added new column with value ${value}`);
        break;

      case 'updateCell':
        if (isNaN(row) || isNaN(col) || isNaN(value)) {
          return Alert.alert('Invalid input', 'Provide valid row, column, and new value.');
        }
        if (row < 0 || row >= matrix.length || col < 0 || col >= matrix[0]?.length) {
          return Alert.alert('Out of bounds', 'Invalid matrix indices.');
        }
        
        const updatedMatrix = matrix.map((r, ri) =>
          ri === row ? r.map((c, ci) => (ci === col ? value : c)) : r
        );
        setMatrix(updatedMatrix);
        setExplanation(`Updated cell [${row}, ${col}] to ${value}`);
        break;
    }

    closeModal();
  };

  const resetMatrix = () => {
    setMatrix([]);
    setExplanation('Matrix cleared. Add rows to build a new matrix.');
  };

  const generateRandomMatrix = () => {
    const rows = Math.floor(Math.random() * 4) + 2;
    const cols = Math.floor(Math.random() * 4) + 2;
    
    const randomMatrix = Array.from({ length: rows }, () =>
      Array.from({ length: cols }, () => Math.floor(Math.random() * 20) + 1)
    );
    
    setMatrix(randomMatrix);
    setExplanation(`Generated ${rows}x${cols} random matrix`);
  };

  const renderMatrix = () => {
    if (matrix.length === 0) {
      return (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Matrix is empty</Text>
          <Text style={styles.emptySubtext}>Add rows to get started</Text>
        </View>
      );
    }

    return (
      <View style={styles.matrix}>
        {matrix.map((row, rIdx) => (
          <View key={rIdx} style={styles.row}>
            {row.map((cell, cIdx) => (
              <View key={`${rIdx}-${cIdx}`} style={styles.box}>
                <Text style={styles.boxText}>{cell}</Text>
                <Text style={styles.coordText}>{rIdx},{cIdx}</Text>
              </View>
            ))}
          </View>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <View style={styles.container}>
          <View style={styles.headerRow}>
            <Text style={styles.header}>🧮 2D Array Operations</Text>
            <TouchableOpacity 
              style={styles.bookmarkToggle} 
              onPress={() => setShowBookmarks(!showBookmarks)}
            >
              <FontAwesome name={showBookmarks ? "bookmark" : "bookmark-o"} size={24} color="#2563eb" />
            </TouchableOpacity>
          </View>

          {/* User Info Section */}
          <View style={styles.authSection}>
            <Text style={styles.welcomeText}>Welcome, {username}!</Text>
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
              <Text style={styles.authButtonText}>Logout</Text>
            </TouchableOpacity>
          </View>

          {renderBookmarksPanel()}

          <Text style={styles.explanation}>{explanation}</Text>

          {/* Matrix Info */}
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>Matrix Information</Text>
            <Text style={styles.infoText}>
              • Dimensions: {matrix.length} × {matrix[0]?.length || 0}{'\n'}
              • Total Elements: {matrix.length * (matrix[0]?.length || 0)}{'\n'}
              • Row Indexes: 0 to {matrix.length - 1}{'\n'}
              • Column Indexes: 0 to {(matrix[0]?.length || 1) - 1}
            </Text>
          </View>

          <View style={styles.buttonRow}>
            <TouchableOpacity 
              style={styles.button} 
              onPress={() => openModal('addRow')}
            >
              <Text style={styles.buttonText}>Add Row</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.button} 
              onPress={() => openModal('addColumn')}
            >
              <Text style={styles.buttonText}>Add Column</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.button} 
              onPress={() => openModal('updateCell')}
            >
              <Text style={styles.buttonText}>Update Cell</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.button, styles.randomButton]} 
              onPress={generateRandomMatrix}
            >
              <Text style={styles.buttonText}>Random Matrix</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.button, styles.bookmarkButton]} 
              onPress={saveBookmark}
            >
              <FontAwesome name="bookmark" size={16} color="white" />
              <Text style={styles.buttonText}> Bookmark</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.button, styles.resetButton]} 
              onPress={resetMatrix}
            >
              <Text style={styles.buttonText}>Clear Matrix</Text>
            </TouchableOpacity>
          </View>

          {/* Matrix Display */}
          <View style={styles.matrixContainer}>
            <Text style={styles.matrixTitle}>Matrix Visualization:</Text>
            {renderMatrix()}
          </View>

          {/* Legend */}
          <View style={styles.legendCard}>
            <Text style={styles.legendTitle}>How to Use:</Text>
            <Text style={styles.legendText}>
              • Add Row: Append a new row with comma-separated values{'\n'}
              • Add Column: Append a new column with the same value in all rows{'\n'}
              • Update Cell: Change a specific cell's value{'\n'}
              • Coordinates show as row,column (e.g., "0,1")
            </Text>
          </View>

          {/* Modal for Input */}
          <Modal visible={modalVisible} animationType="slide" transparent>
            <View style={styles.modalOverlay}>
              <View style={styles.modalContainer}>
                <Text style={styles.modalTitle}>
                  {modalType === 'addRow' ? 'ADD ROW' : 
                   modalType === 'addColumn' ? 'ADD COLUMN' : 'UPDATE CELL'}
                </Text>

                {modalType === 'addRow' ? (
                  <>
                    <Text style={styles.modalHint}>
                      {matrix.length > 0 ? `Enter ${matrix[0].length} comma-separated values` : 'Enter comma-separated values'}
                    </Text>
                    <TextInput
                      placeholder='e.g., 1,2,3,4'
                      value={inputValue}
                      onChangeText={setInputValue}
                      style={styles.modalInput}
                      keyboardType="numbers-and-punctuation"
                    />
                  </>
                ) : modalType === 'addColumn' ? (
                  <TextInput
                    placeholder="Value for new column"
                    value={inputValue}
                    onChangeText={setInputValue}
                    keyboardType="numeric"
                    style={styles.modalInput}
                  />
                ) : (
                  <>
                    <TextInput
                      placeholder="Row Index"
                      value={rowIndex}
                      onChangeText={setRowIndex}
                      keyboardType="numeric"
                      style={styles.modalInput}
                    />
                    <TextInput
                      placeholder="Column Index"
                      value={colIndex}
                      onChangeText={setColIndex}
                      keyboardType="numeric"
                      style={styles.modalInput}
                    />
                    <TextInput
                      placeholder="New Value"
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
const BOOKMARK_COLOR = '#f59e0b';
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  header: {
    fontSize: 28,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  authSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    padding: 12,
    backgroundColor: 'white',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  welcomeText: {
    fontSize: 16,
    fontWeight: '600',
    color: PRIMARY_COLOR,
  },
  logoutButton: {
    backgroundColor: '#ef4444',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  authButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  bookmarkToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
  },
  explanation: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 20,
    textAlign: 'center',
    fontStyle: 'italic',
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
    marginBottom: 8,
    color: PRIMARY_COLOR,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
  buttonRow: {
    ...(Platform.OS === "web" ? {
      flexDirection: 'row',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: 8,
    } : {
      flexDirection: 'column',
    }),
    marginBottom: 16,
  },
  button: {
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    ...(Platform.OS === "web" ? {
      minWidth: 100,
      flex: 1,
    } : {
      marginBottom: 12,
    }),
    flexDirection: 'row',
    justifyContent: 'center',
  },
  resetButton: {
    backgroundColor: '#ef4444',
  },
  randomButton: {
    backgroundColor: '#8b5cf6',
  },
  bookmarkButton: {
    backgroundColor: BOOKMARK_COLOR,
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
  },
  matrixContainer: {
    marginTop: 24,
    marginBottom: 16,
    alignItems: 'center',
  },
  matrixTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  matrix: {
    alignItems: 'center',
  },
  row: {
    flexDirection: 'row',
    marginBottom: BOX_MARGIN,
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    backgroundColor: 'white',
    marginHorizontal: BOX_MARGIN / 2,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  boxText: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  coordText: {
    position: 'absolute',
    bottom: 4,
    fontSize: 10,
    color: '#6b7280',
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
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
  legendText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
  bookmarksPanel: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    maxHeight: 200,
  },
  bookmarksTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: BOOKMARK_COLOR,
    textAlign: 'center',
  },
  bookmarksList: {
    maxHeight: 140,
  },
  bookmarkItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  bookmarkContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  bookmarkIndex: {
    fontWeight: 'bold',
    color: BOOKMARK_COLOR,
    marginRight: 8,
    width: 30,
  },
  bookmarkMatrix: {
    flex: 1,
    color: '#374151',
    fontSize: 12,
  },
  deleteBookmark: {
    padding: 4,
  },
  noBookmarks: {
    textAlign: 'center',
    color: '#6b7280',
    fontStyle: 'italic',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    backgroundColor: 'white',
    width: Platform.OS === "web" ? '50%' : '85%',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
  },
  modalHint: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
    textAlign: 'center',
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
    width: '100%',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#6b7280',
  },
});