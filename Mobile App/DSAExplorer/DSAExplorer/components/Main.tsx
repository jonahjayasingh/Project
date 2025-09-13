import React, { useState, useEffect, useCallback } from 'react';
import {
  Text,
  FlatList,
  TouchableOpacity,
  Image,
  Dimensions,
  Platform,
  Alert,
  View,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Feather } from '@expo/vector-icons';

// Define valid screen names for type safety
type ScreenName =
  | 'LinearSearch'
  | 'BinarySearch'
  | 'BubbleSort'
  | 'SelectionSort'
  | 'InsertionSort'
  | 'MergeSort'
  | 'QuickSort'
  | 'OneDArrayOperations'
  | 'TwoDArrayOperations'
  | 'StringManipulations'
  | 'SinglyLinkedList'
  | 'DoubleLinkedList'
  | 'CircularSingleLinkedList'
  | 'CircularDoublyLinkedList'
  | 'Stack'
  | 'Queue'
  | 'InorderTraversal'
  | 'PreorderTraversal'
  | 'PostorderTraversal'
  | 'BFSTraversal'
  | 'DFS';

interface AlgorithmItem {
  id: string;
  title: string;
  image: any;
  screenName: ScreenName;
}

interface Bookmark {
  id: number;
  algorithm: string;
  user_id: number;
  created_at?: string;
}

const API_BASE_URL = Platform.OS === 'web' ? 'http://127.0.0.1:8000' : 'http://10.0.2.2:8000';

const algorithms: AlgorithmItem[] = [
  { id: '1', title: 'Linear Search', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'LinearSearch' },
  { id: '2', title: 'Binary Search', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'BinarySearch' },
  { id: '3', title: 'Bubble Sort', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'BubbleSort' },
  { id: '4', title: 'Selection Sort', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'SelectionSort' },
  { id: '5', title: 'Insertion Sort', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'InsertionSort' },
  { id: '6', title: 'Merge Sort', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'MergeSort' },
  { id: '7', title: 'Quick Sort', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'QuickSort' },
  { id: '8', title: '1D Array Operations', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'OneDArrayOperations' },
  { id: '9', title: '2D Array Operations', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'TwoDArrayOperations' },
  { id: '10', title: 'String Manipulations', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'StringManipulations' },
  { id: '11', title: 'Singly Linked List', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'SinglyLinkedList' },
  { id: '12', title: 'Doubly Linked List', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'DoubleLinkedList' },
  { id: '13', title: 'Circular Singly Linked List', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'CircularSingleLinkedList' },
  { id: '14', title: 'Circular Doubly Linked List', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'CircularDoublyLinkedList' },
  { id: '15', title: 'Stack', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'Stack' },
  { id: '16', title: 'Queue', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'Queue' },
  { id: '17', title: 'Inorder Traversal', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'InorderTraversal' },
  { id: '18', title: 'Preorder Traversal', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'PreorderTraversal' },
  { id: '19', title: 'Postorder Traversal', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'PostorderTraversal' },
  { id: '20', title: 'Breadth-First Search (BFS)', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'BFSTraversal' },
  { id: '21', title: 'Depth-First Search (DFS)', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'DFS' },
];

const CARD_MARGIN = 8;
const ICON_SIZE = 48;

export const Main = () => {
  const navigation = useNavigation();
  const [bookmarkedItems, setBookmarkedItems] = useState<string[]>([]);
  const [serverBookmarks, setServerBookmarks] = useState<Bookmark[]>([]);
  const [showBookmarksOnly, setShowBookmarksOnly] = useState(false);
  const [userName, setUserName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [hasLoadedInitialBookmarks, setHasLoadedInitialBookmarks] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const screenWidth = Dimensions.get('window').width;
  const isWeb = Platform.OS === 'web';
  const effectiveColumns = isWeb ? 5 : 2;
  const CARD_WIDTH = isWeb
    ? Math.max(120, (screenWidth - CARD_MARGIN * (effectiveColumns + 1)) / effectiveColumns)
    : (screenWidth - CARD_MARGIN * 3) / effectiveColumns;

  // Memoized functions to prevent unnecessary re-renders
  const redirectToLogin = useCallback(() => {
    if (Platform.OS === 'web') {
      window.location.href = '/login';
    } else {
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' as never }],
      });
    }
  }, [navigation]);

  const refreshTokenAndRetry = useCallback(async (): Promise<boolean> => {
    try {
      const refreshToken = await AsyncStorage.getItem('refreshToken');
      if (!refreshToken) {
        redirectToLogin();
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        await AsyncStorage.setItem('accessToken', data.access_token);
        return true;
      } else {
        redirectToLogin();
        return false;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      redirectToLogin();
      return false;
    }
  }, [redirectToLogin]);

  const loadBookmarksFromServer = useCallback(async () => {
    if (isLoading || hasLoadedInitialBookmarks) return;

    try {
      setIsLoading(true);
      setError(null);

      const accessToken = await AsyncStorage.getItem('accessToken');
      if (!accessToken) {
        setHasLoadedInitialBookmarks(true);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/getbookmarks`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const bookmarks = await response.json();
        setServerBookmarks(bookmarks);
        const algorithmIds = bookmarks.map((bookmark: Bookmark) => bookmark.algorithm);
        setBookmarkedItems(algorithmIds);
        setHasLoadedInitialBookmarks(true);
      } else if (response.status === 401) {
        const refreshed = await refreshTokenAndRetry();
        if (refreshed && !hasLoadedInitialBookmarks) {
          // Retry only if token refresh was successful and we haven't loaded yet
          await loadBookmarksFromServer();
        }
      } else {
        setError('Failed to load bookmarks');
        setHasLoadedInitialBookmarks(true);
      }
    } catch (error) {
      console.error('Error loading bookmarks from server:', error);
      setError('Network error. Please try again.');
      setHasLoadedInitialBookmarks(true);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, hasLoadedInitialBookmarks, refreshTokenAndRetry]);

  const loadUserInfo = useCallback(async () => {
    try {
      const email = await AsyncStorage.getItem('userName');
      if (email) {
        setUserName(email);
      }
    } catch (error) {
      console.error('Error loading user info:', error);
    }
  }, []);

  // Load bookmarks and user info on component mount
  useEffect(() => {
    loadUserInfo();
    loadBookmarksFromServer();
  }, [loadUserInfo, loadBookmarksFromServer]);

  const toggleBookmark = async (algorithmId: string) => {
    try {
      const accessToken = await AsyncStorage.getItem('accessToken');
      if (!accessToken) {
        Alert.alert('Error', 'Please login to use bookmarks');
        return;
      }

      const existingBookmark = serverBookmarks.find(
        (bookmark) => bookmark.algorithm === algorithmId
      );

      if (existingBookmark) {
        const response = await fetch(
          `${API_BASE_URL}/deletebookmark/${existingBookmark.id}`,
          {
            method: 'DELETE',
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (response.ok) {
          setServerBookmarks(
            serverBookmarks.filter((b) => b.id !== existingBookmark.id)
          );
          setBookmarkedItems(
            bookmarkedItems.filter((id) => id !== algorithmId)
          );
        } else if (response.status === 401) {
          const refreshed = await refreshTokenAndRetry();
          if (refreshed) {
            // Retry the operation after token refresh
            toggleBookmark(algorithmId);
          }
        } else {
          Alert.alert('Error', 'Failed to remove bookmark');
        }
      } else {
        const response = await fetch(`${API_BASE_URL}/addbookmark`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            algorithm: algorithmId,
          }),
        });

        if (response.ok) {
          const newBookmark = await response.json();
          setServerBookmarks([...serverBookmarks, newBookmark]);
          setBookmarkedItems([...bookmarkedItems, algorithmId]);
        } else if (response.status === 401) {
          const refreshed = await refreshTokenAndRetry();
          if (refreshed) {
            // Retry the operation after token refresh
            toggleBookmark(algorithmId);
          }
        } else {
          Alert.alert('Error', 'Failed to add bookmark');
        }
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
      Alert.alert('Error', 'Network error. Please try again.');
    }
  };

  const handleLogout = async () => {
    console.log('Logout pressed');

    if (Platform.OS === 'web') {
      const confirmLogout = window.confirm('Are you sure you want to logout?');
      if (!confirmLogout) return;

      setIsLoggingOut(true);
      try {
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        const accessToken = await AsyncStorage.getItem('accessToken');

        if (refreshToken && accessToken) {
          try {
            await fetch(`${API_BASE_URL}/logout`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
          } catch (error) {
            console.error('Logout API error:', error);
          }
        }

        await AsyncStorage.multiRemove([
          'accessToken',
          'refreshToken',
          'username',
        ]);

        window.location.replace('/login');
      } catch (error) {
        console.error('Error during logout:', error);
        await AsyncStorage.multiRemove([
          'accessToken',
          'refreshToken',
          'userName',
        ]);
        window.location.replace('/login');
      } finally {
        setIsLoggingOut(false);
      }
    } else {
      Alert.alert(
        'Logout',
        'Are you sure you want to logout?',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Logout',
            style: 'destructive',
            onPress: async () => {
              setIsLoggingOut(true);
              try {
                const refreshToken = await AsyncStorage.getItem('refreshToken');
                const accessToken = await AsyncStorage.getItem('accessToken');

                if (refreshToken && accessToken) {
                  try {
                    await fetch(`${API_BASE_URL}/logout`, {
                      method: 'POST',
                      headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({ refresh_token: refreshToken }),
                    });
                  } catch (error) {
                    console.error('Logout API error:', error);
                  }
                }

                await AsyncStorage.multiRemove([
                  'accessToken',
                  'refreshToken',
                  'userName',
                ]);

                navigation.reset({
                  index: 0,
                  routes: [{ name: 'Login' as never }],
                });
              } catch (error) {
                console.error('Error during logout:', error);
                await AsyncStorage.multiRemove([
                  'accessToken',
                  'refreshToken',
                  'userName',
                ]);
                navigation.reset({
                  index: 0,
                  routes: [{ name: 'Login' as never }],
                });
              } finally {
                setIsLoggingOut(false);
              }
            },
          },
        ],
        { cancelable: true }
      );
    }
  };

  const filteredAlgorithms = showBookmarksOnly
    ? algorithms.filter(item => bookmarkedItems.includes(item.id))
    : algorithms;

  const renderItem = ({ item }: { item: AlgorithmItem }) => (
    <TouchableOpacity
      className="bg-white p-3 items-center justify-center"
      activeOpacity={0.9}
      style={{
        width: CARD_WIDTH,
        marginBottom: CARD_MARGIN,
        marginRight: CARD_MARGIN,
        minWidth: 80,
      }}
      onPress={() => navigation.navigate(item.screenName as never)}
    >
      {/* Bookmark icon */}
      <TouchableOpacity
        className="absolute top-1 right-1 z-10 p-1"
        onPress={() => toggleBookmark(item.id)}
        activeOpacity={0.7}
        disabled={isLoading}
        style={isWeb ? { cursor: 'pointer' } : {}}
      >
        <Feather
          name="bookmark"
          size={16}
          color={bookmarkedItems.includes(item.id) ? '#4F46E5' : '#D1D5DB'}
          fill={bookmarkedItems.includes(item.id) ? '#4F46E5' : 'none'}
        />
      </TouchableOpacity>

      {/* Icon */}
      <Image
        source={item.image}
        style={{
          width: ICON_SIZE,
          height: ICON_SIZE,
          resizeMode: 'contain',
          marginBottom: 6,
        }}
      />

      {/* Title */}
      <Text
        className="text-gray-800 text-xs font-medium text-center leading-tight"
        numberOfLines={2}
      >
        {item.title}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView
      className={`flex-1 bg-white ${isWeb ? 'px-6 pt-6' : 'px-3'} ${
        Platform.OS === 'ios' ? 'pt-0' : 'pt-6'
      }`}
    >
      {/* Header */}
      <View className="flex-row justify-between items-center mb-6">
        <View>
          <Text className="text-xl font-bold text-gray-900">DSAExplorer</Text>
          {userName ? (
            <Text className="text-gray-500 text-xs mt-1">Welcome, {userName}</Text>
          ) : null}
        </View>
        <TouchableOpacity
          onPress={handleLogout}
          className="p-1.5"
          activeOpacity={0.7}
          disabled={isLoggingOut}
          style={isWeb ? { cursor: 'pointer' } : {}}
        >
          {isLoggingOut ? (
            <ActivityIndicator size="small" color="#4F46E5" />
          ) : (
            <Feather name="log-out" size={18} color="#6B7280" />
          )}
        </TouchableOpacity>
      </View>

      {/* Filter toggle and error message */}
      <View className="flex-row items-center justify-between mb-2">
        <TouchableOpacity
          className="flex-row items-center py-1"
          onPress={() => setShowBookmarksOnly(!showBookmarksOnly)}
          activeOpacity={0.8}
          style={isWeb ? { cursor: 'pointer' } : {}}
        >
          <Feather
            name="bookmark"
            size={16}
            color={showBookmarksOnly ? '#4F46E5' : '#9CA3AF'}
            fill={showBookmarksOnly ? '#4F46E5' : 'none'}
          />
          <Text className={`ml-1 text-xs font-medium ${
            showBookmarksOnly ? 'text-indigo-600' : 'text-gray-500'
          }`}>
            {showBookmarksOnly ? 'Bookmarks' : 'All'}
          </Text>
        </TouchableOpacity>

        {error && (
          <Text className="text-red-500 text-xs">{error}</Text>
        )}
      </View>

      {/* Loading state */}
      {isLoading && (
        <View className="flex-row justify-center items-center py-3">
          <ActivityIndicator size="small" color="#4F46E5" />
          <Text className="text-gray-500 text-xs ml-1">Loading...</Text>
        </View>
      )}

      {/* Algorithm list */}
      <FlatList
        data={filteredAlgorithms}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        numColumns={effectiveColumns}
        showsVerticalScrollIndicator={false}
        columnWrapperStyle={{ justifyContent: 'flex-start', gap: CARD_MARGIN }}
        contentContainerStyle={{
          paddingBottom: isWeb ? 64 : 48,
          paddingHorizontal: isWeb ? 0 : 4,
        }}
        ListEmptyComponent={
          <View className="flex-1 justify-center items-center py-10 px-4">
            <Feather name="bookmark" size={48} color="#F3F4F6" />
            <Text className="text-gray-400 text-xs text-center mt-3 max-w-xs">
              {showBookmarksOnly
                ? 'No algorithms bookmarked yet.\nTap the bookmark icon to save favorites.'
                : 'No algorithms available.'}
            </Text>
          </View>
        }
      />

      {/* Retry button for errors */}
      {error && !isLoading && (
        <View className="absolute bottom-4 left-0 right-0 items-center">
          <TouchableOpacity
            onPress={loadBookmarksFromServer}
            className="bg-indigo-600 px-4 py-2 rounded-lg"
            activeOpacity={0.7}
          >
            <Text className="text-white text-sm">Retry</Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
};