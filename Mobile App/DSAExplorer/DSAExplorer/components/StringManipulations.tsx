import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  StatusBar,
  Platform,
  ActivityIndicator
} from 'react-native';
import { useAuth } from 'AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { FontAwesome } from '@expo/vector-icons';

const API_BASE_URL = Platform.OS === 'web' ? 'http://127.0.0.1:8000' : 'http://10.0.2.2:8000';
const ALGORITHM_ID = '10'; // String Manipulations ID

export function StringManipulations() {
  const [inputText, setInputText] = useState('');
  const [concatenateText, setConcatenateText] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [loadingBookmark, setLoadingBookmark] = useState(false);
  const { user } = useAuth();

  const stringOperations = {
    reverse: (str: string): string => {
      return str.split('').reverse().join('');
    },
    uppercase: (str: string): string => {
      return str.toUpperCase();
    },
    lowercase: (str: string): string => {
      return str.toLowerCase();
    },
    palindrome: (str: string): string => {
      const cleaned = str.replace(/[^A-Za-z0-9]/g, '').toLowerCase();
      return cleaned === cleaned.split('').reverse().join('') 
        ? 'Yes, it is a palindrome!' 
        : 'No, not a palindrome';
    },
    vowels: (str: string): string => {
      const vowels = str.match(/[aeiouAEIOU]/g);
      return `Vowel count: ${vowels ? vowels.length : 0}`;
    },
    words: (str: string): string => {
      const words = str.trim().split(/\s+/).filter(word => word.length > 0);
      return `Word count: ${words.length}`;
    },
    characters: (str: string): string => {
      return `Character count: ${str.length}`;
    },
    titlecase: (str: string): string => {
      return str.replace(/\w\S*/g, (txt) => {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
    },
    concatenate: (str1: string, str2: string): string => {
      return str1 + str2;
    }
  };

  // Check if this algorithm is bookmarked
  const checkBookmarkStatus = async () => {
    if (!user) {
      setIsBookmarked(false);
      return;
    }

    try {
      // First try to get all bookmarks and check if our algorithm is in the list
      const response = await fetch(`${API_BASE_URL}/getbookmarks`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${user.accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const bookmarks = await response.json();
        const isBookmarked = bookmarks.some((bookmark: any) => 
          bookmark.algorithm === ALGORITHM_ID || bookmark.algorithm_id === ALGORITHM_ID
        );
        setIsBookmarked(isBookmarked);
      } else {
        console.error('Failed to fetch bookmarks:', response.status);
        setIsBookmarked(false);
      }
    } catch (error) {
      console.error('Error checking bookmark status:', error);
      setIsBookmarked(false);
    }
  };

  // Check bookmark status on component mount and when user changes
  useEffect(() => {
    checkBookmarkStatus();
  }, [user]);

  const handleOperation = (op: string) => {
    if (inputText.trim() === '') {
      Alert.alert('Input Required', 'Please enter some text to perform operations');
      return;
    }
    
    setOperation(op);
    
    if (op === 'concatenate') {
      if (concatenateText.trim() === '') {
        Alert.alert('Second Text Required', 'Please enter text to concatenate');
        return;
      }
      setResult(stringOperations.concatenate(inputText, concatenateText));
    } else {
      setResult(stringOperations[op as keyof typeof stringOperations](inputText));
    }
  };

  const toggleBookmark = async () => {
    if (!user) {
      Alert.alert('Authentication Required', 'Please login to bookmark algorithms');
      return;
    }

    setLoadingBookmark(true);
    try {
      if (isBookmarked) {
        // Remove bookmark - first we need to find the bookmark ID
        const bookmarksResponse = await fetch(`${API_BASE_URL}/getbookmarks`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${user.accessToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (bookmarksResponse.ok) {
          const bookmarks = await bookmarksResponse.json();
          const bookmark = bookmarks.find((b: any) => 
            b.algorithm === ALGORITHM_ID || b.algorithm_id === ALGORITHM_ID
          );
          
          if (bookmark) {
            const deleteResponse = await fetch(`${API_BASE_URL}/deletebookmark/${bookmark.id}`, {
              method: 'DELETE',
              headers: {
                'Authorization': `Bearer ${user.accessToken}`,
              },
            });

            if (deleteResponse.ok) {
              setIsBookmarked(false);
              Alert.alert('Success', 'Bookmark removed successfully!');
            } else {
              Alert.alert('Error', 'Failed to remove bookmark');
            }
          }
        } else {
          Alert.alert('Error', 'Failed to fetch bookmarks');
        }
      } else {
        // Add bookmark
        const response = await fetch(`${API_BASE_URL}/addbookmark`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${user.accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            algorithm_id: ALGORITHM_ID
          }),
        });

        if (response.ok) {
          setIsBookmarked(true);
          Alert.alert('Success', 'Algorithm bookmarked successfully!');
        } else {
          Alert.alert('Error', 'Failed to add bookmark');
        }
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
      Alert.alert('Error', 'Failed to update bookmark');
    } finally {
      setLoadingBookmark(false);
    }
  };

  const clearAll = () => {
    setInputText('');
    setConcatenateText('');
    setResult(null);
    setOperation(null);
  };

  const OperationButton = ({ title, op, icon }: { title: string, op: string, icon: string }) => (
    <TouchableOpacity 
      style={[
        styles.operationButton, 
        operation === op && styles.activeOperation
      ]} 
      onPress={() => handleOperation(op)}
    >
      <Text style={styles.operationIcon}>{icon}</Text>
      <Text style={styles.operationText}>{title}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>🔤 String Manipulation</Text>
          {user && (
            <TouchableOpacity 
              onPress={toggleBookmark}
              style={styles.bookmarkButton}
              disabled={loadingBookmark}
            >
              {loadingBookmark ? (
                <ActivityIndicator size="small" color="#2563eb" />
              ) : (
                <FontAwesome 
                  name={isBookmarked ? "bookmark" : "bookmark-o"} 
                  size={24} 
                  color="#2563eb" 
                />
              )}
            </TouchableOpacity>
          )}
        </View>
        
        <Text style={styles.subtitle}>Transform and analyze your text</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Enter your text:</Text>
          <TextInput
            style={styles.input}
            placeholder="Type or paste your text here..."
            value={inputText}
            onChangeText={setInputText}
            multiline
            numberOfLines={4}
          />
          <Text style={styles.charCount}>
            {inputText.length} character{inputText.length !== 1 ? 's' : ''}
          </Text>
        </View>

        {operation === 'concatenate' && (
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Text to concatenate:</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter text to add to the end..."
              value={concatenateText}
              onChangeText={setConcatenateText}
              multiline
              numberOfLines={3}
            />
          </View>
        )}

        <View style={styles.operationsGrid}>
          <OperationButton title="Reverse" op="reverse" icon="🔄" />
          <OperationButton title="Uppercase" op="uppercase" icon="🔠" />
          <OperationButton title="Lowercase" op="lowercase" icon="🔡" />
          <OperationButton title="Title Case" op="titlecase" icon="🏷️" />
          <OperationButton title="Concatenate" op="concatenate" icon="➕" />
          <OperationButton title="Palindrome" op="palindrome" icon="📖" />
          <OperationButton title="Count Vowels" op="vowels" icon="🔊" />
          <OperationButton title="Count Words" op="words" icon="📝" />
          <OperationButton title="Count Chars" op="characters" icon="🔢" />
        </View>

        {result !== null && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultLabel}>
              {operation ? operation.charAt(0).toUpperCase() + operation.slice(1) : 'Result'}:
            </Text>
            <View style={styles.resultBox}>
              <Text style={styles.resultText}>{result}</Text>
            </View>
          </View>
        )}
        
        <View style={styles.clearButtonContainer}>
          <TouchableOpacity 
            style={[styles.button, styles.clearButton]} 
            onPress={clearAll}
            disabled={!inputText && !result && !concatenateText}
          >
            <Text style={styles.buttonText}>🗑️ Clear All</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>💡 Tips:</Text>
          <Text style={styles.infoText}>
            • Use Reverse to flip your text{'\n'}
            • Concatenate joins two texts together{'\n'}
            • Palindrome check ignores spaces and punctuation{'\n'}
            • Title Case capitalizes each word{'\n'}
            • Word count ignores extra spaces
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const SECONDARY_COLOR = '#8b5cf6';
const SUCCESS_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight,
  },
  container: {
    flexGrow: 1,
    padding: 24,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    fontSize: 32,
    fontWeight: '800',
    color: PRIMARY_COLOR,
    flex: 1,
  },
  bookmarkButton: {
    padding: 8,
    marginLeft: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 32,
    fontStyle: 'italic',
  },
  inputContainer: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    minHeight: 120,
    borderColor: '#d1d5db',
    borderWidth: 2,
    borderRadius: 16,
    padding: 16,
    fontSize: 16,
    backgroundColor: 'white',
    color: '#1f2937',
    textAlignVertical: 'top',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  charCount: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'right',
    marginTop: 8,
  },
  operationsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-evenly',
    marginBottom: 24,
    gap: Platform.OS === "web" ? 4 : 6,
  },
  operationButton: {
    width: Platform.OS === "web" ? '22%' : '48%',
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    marginBottom: 8,
  },
  activeOperation: {
    borderColor: PRIMARY_COLOR,
    backgroundColor: '#eff6ff',
    transform: [{ scale: 1.02 }],
  },
  operationIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  operationText: {
    fontSize: 14,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  resultContainer: {
    marginBottom: 24,
  },
  resultLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 12,
  },
  resultBox: {
    backgroundColor: '#e0e7ff',
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  resultText: {
    fontSize: 18,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  button: {
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: PRIMARY_COLOR,
    shadowOpacity: 0.3,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
  },
  clearButtonContainer: {
    width: '100%',
    alignItems: 'center',
  },
  clearButton: {
    backgroundColor: '#6b7280',
    ...(Platform.OS === 'web' && {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-around',
      width: '20%',
    })
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 16,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
});