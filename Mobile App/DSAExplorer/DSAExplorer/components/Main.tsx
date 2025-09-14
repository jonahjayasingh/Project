import React, { useState, useCallback, useEffect } from 'react';
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
  StyleSheet,
  TextInput,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Feather, MaterialIcons, FontAwesome } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from 'AuthContext';

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
  category: string;
  image: any;
  screenName: ScreenName;
  color: string;
  isBookmarked?: boolean;
  bookmarkId?: number; // To store the bookmark ID from the server
}

interface Bookmark {
  id: number;
  algorithm_id: string; // Changed from algorithm_id to algorithm
  user_id: number;
}

const API_BASE_URL = Platform.OS === 'web' ? 'http://127.0.0.1:8000' : 'http://10.0.2.2:8000';

const algorithms: AlgorithmItem[] = [
  { id: '1', title: 'Linear Search', category: 'Searching', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'LinearSearch', color: '#4F46E5' },
  { id: '2', title: 'Binary Search', category: 'Searching', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'BinarySearch', color: '#7C3AED' },
  { id: '3', title: 'Bubble Sort', category: 'Sorting', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'BubbleSort', color: '#DB2777' },
  { id: '4', title: 'Selection Sort', category: 'Sorting', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'SelectionSort', color: '#EC4899' },
  { id: '5', title: 'Insertion Sort', category: 'Sorting', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'InsertionSort', color: '#F43F5E' },
  { id: '6', title: 'Merge Sort', category: 'Sorting', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'MergeSort', color: '#F59E0B' },
  { id: '7', title: 'Quick Sort', category: 'Sorting', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'QuickSort', color: '#D97706' },
  { id: '8', title: '1D Array Operations', category: 'Arrays', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'OneDArrayOperations', color: '#10B981' },
  { id: '9', title: '2D Array Operations', category: 'Arrays', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'TwoDArrayOperations', color: '#059669' },
  { id: '10', title: 'String Manipulations', category: 'Strings', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'StringManipulations', color: '#0EA5E9' },
  { id: '11', title: 'Singly Linked List', category: 'Linked Lists', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'SinglyLinkedList', color: '#6366F1' },
  { id: '12', title: 'Doubly Linked List', category: 'Linked Lists', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'DoubleLinkedList', color: '#8B5CF6' },
  { id: '13', title: 'Circular Singly Linked List', category: 'Linked Lists', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'CircularSingleLinkedList', color: '#A855F7' },
  { id: '14', title: 'Circular Doubly Linked List', category: 'Linked Lists', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'CircularDoublyLinkedList', color: '#BFDBFE' },
  { id: '15', title: 'Stack', category: 'Data Structures', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'Stack', color: '#F97316' },
  { id: '16', title: 'Queue', category: 'Data Structures', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'Queue', color: '#FB923C' },
  { id: '17', title: 'Inorder Traversal', category: 'Trees', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'InorderTraversal', color: '#22C55E' },
  { id: '18', title: 'Preorder Traversal', category: 'Trees', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'PreorderTraversal', color: '#16A34A' },
  { id: '19', title: 'Postorder Traversal', category: 'Trees', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'PostorderTraversal', color: '#15803D' },
  { id: '20', title: 'Breadth-First Search (BFS)', category: 'Graphs', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'BFSTraversal', color: '#06B6D4' },
  { id: '21', title: 'Depth-First Search (DFS)', category: 'Graphs', image: require('../assets/AlgorithmIcons/LinearSearchImage.png'), screenName: 'DFS', color: '#0891B2' },
].map(item => ({ ...item, isBookmarked: false }));

const CARD_MARGIN = 12;
const ICON_SIZE = 48;

export const Main = () => {
  const navigation = useNavigation();
  const { user, logout: authLogout, loading: authLoading } = useAuth();
  const [userName, setUserName] = useState('');
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [algorithmList, setAlgorithmList] = useState<AlgorithmItem[]>(algorithms);
  const [showBookmarks, setShowBookmarks] = useState(false);
  const [loadingBookmarks, setLoadingBookmarks] = useState(false);

  const screenWidth = Dimensions.get('window').width;
  const isWeb = Platform.OS === 'web';
  const effectiveColumns = isWeb ? (screenWidth > 1200 ? 4 : screenWidth > 900 ? 3 : 2) : 2;
  const CARD_WIDTH = isWeb
    ? Math.max(180, (screenWidth - CARD_MARGIN * (effectiveColumns + 1) - 40) / effectiveColumns)
    : (screenWidth - CARD_MARGIN * 3) / 2;

  // Get unique categories
  const categories = ['All', ...Array.from(new Set(algorithms.map(item => item.category)))];

  // Filter algorithms based on selected category and search query
  const filteredAlgorithms = algorithmList.filter(item => {
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBookmark = showBookmarks ? item.isBookmarked : true;
    return matchesCategory && matchesSearch && matchesBookmark;
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      console.log('User not authenticated, redirecting to login');
      if (Platform.OS === 'web') {
        window.location.href = '/login';
      } else {
        navigation.reset({
          index: 0,
          routes: [{ name: 'Login' as never }],
        });
      }
    }
  }, [user, authLoading, navigation]);

  // Initialize the component
  useEffect(() => {
    const initializeApp = async () => {
      if (user) {
        try {
          setUserName(user.username);
          await fetchBookmarks();
        } catch (error) {
          console.error('Initialization error:', error);
        }
      }
    };

    initializeApp();
  }, [user]);

  // Fetch user's bookmarks from the server
  const fetchBookmarks = useCallback(async () => {
    try {
      setLoadingBookmarks(true);
      
      if (!user) {
        console.log('No user found');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/getbookmarks`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${user.accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const bookmarks: Bookmark[] = await response.json();
        console.log('Bookmarks received:', bookmarks);
        
        // Update algorithm list with bookmark status
        setAlgorithmList(prevList => 
          prevList.map(item => {
            const bookmark = bookmarks.find(b => b.algorithm_id === item.id); // Changed from algorithm_id to algorithm
            return bookmark 
              ? { ...item, isBookmarked: true, bookmarkId: bookmark.id } 
              : { ...item, isBookmarked: false, bookmarkId: undefined };
          })
        );
      } else if (response.status === 401) {
        // Token expired, redirect to login
        authLogout();
      } else {
        console.error('Failed to fetch bookmarks:', response.status);
      }
    } catch (error) {
      console.error('Error fetching bookmarks:', error);
    } finally {
      setLoadingBookmarks(false);
    }
  }, [user, authLogout]);

  // Add bookmark to server
  const addBookmark = async (item: AlgorithmItem) => {
    try {
      if (!user) {
        Alert.alert('Error', 'Please login to bookmark algorithms');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/addbookmark`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          algorithm_id: item.id
        }),
      });

      if (response.ok) {
        const newBookmark = await response.json();
        setAlgorithmList(prevList => 
          prevList.map(algo => 
            algo.id === item.id 
              ? { ...algo, isBookmarked: true, bookmarkId: newBookmark.id } 
              : algo
          )
        );
      } else if (response.status === 401) {
        authLogout();
      } else {
        console.error('Failed to add bookmark:', response.status);
        Alert.alert('Error', 'Failed to bookmark algorithm');
      }
    } catch (error) {
      console.error('Error adding bookmark:', error);
      Alert.alert('Error', 'Failed to bookmark algorithm');
    }
  };

  // Delete bookmark from server
  const deleteBookmark = async (item: AlgorithmItem) => {
    try {
      if (!user || !item.bookmarkId) {
        console.error('No user found or no bookmark ID');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/deletebookmark/${item.bookmarkId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${user.accessToken}`,
        },
      });

      if (response.ok) {
        setAlgorithmList(prevList => 
          prevList.map(algo => 
            algo.id === item.id 
              ? { ...algo, isBookmarked: false, bookmarkId: undefined } 
              : algo
          )
        );
      } else if (response.status === 401) {
        authLogout();
      } else {
        console.error('Failed to delete bookmark:', response.status);
        Alert.alert('Error', 'Failed to remove bookmark');
      }
    } catch (error) {
      console.error('Error deleting bookmark:', error);
      Alert.alert('Error', 'Failed to remove bookmark');
    }
  };

  // Toggle bookmark status
  const toggleBookmark = async (item: AlgorithmItem) => {
    if (!user) {
      Alert.alert('Authentication Required', 'Please login to bookmark algorithms');
      return;
    }
    
    if (item.isBookmarked) {
      await deleteBookmark(item);
    } else {
      await addBookmark(item);
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

        await authLogout();

        window.location.replace('/login');
      } catch (error) {
        console.error('Error during logout:', error);
        await authLogout();
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

                await authLogout();

                navigation.reset({
                  index: 0,
                  routes: [{ name: 'Login' as never }],
                });
              } catch (error) {
                console.error('Error during logout:', error);
                await authLogout();
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

  const renderItem = ({ item }: { item: AlgorithmItem }) => (
    <TouchableOpacity
      activeOpacity={0.9}
      style={[
        styles.card,
        {
          width: CARD_WIDTH,
          marginBottom: CARD_MARGIN,
          marginRight: CARD_MARGIN,
          shadowColor: item.color,
          backgroundColor: '#fff',
        },
      ]}
      onPress={() => navigation.navigate(item.screenName as never)}
    >
      <LinearGradient
        colors={[item.color, `${item.color}DD`]}
        style={styles.cardHeader}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <Text style={styles.cardCategory}>{item.category}</Text>
        <TouchableOpacity 
          onPress={(e) => {
            e.stopPropagation();
            toggleBookmark(item);
          }}
          style={styles.bookmarkButton}
          disabled={loadingBookmarks}
        >
          {loadingBookmarks ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <FontAwesome 
              name={item.isBookmarked ? "bookmark" : "bookmark-o"} 
              size={16} 
              color="#fff" 
            />
          )}
        </TouchableOpacity>
      </LinearGradient>
      
      <View style={styles.cardContent}>
        <View style={[styles.iconContainer, { backgroundColor: `${item.color}15` }]}>
          <Image
            source={item.image}
            style={styles.cardIcon}
          />
        </View>

        <Text style={styles.cardTitle} numberOfLines={2}>
          {item.title}
        </Text>
        
        <View style={styles.cardButton}>
          <Text style={styles.cardButtonText}>Explore</Text>
          <Feather name="arrow-right" size={14} color="#4F46E5" />
        </View>
      </View>
    </TouchableOpacity>
  );

  // Show loading screen while checking authentication
  if (authLoading) {
    return (
      <SafeAreaView style={[styles.container, styles.centerContent]}>
        <ActivityIndicator size="large" color="#4F46E5" />
        <Text style={styles.loadingText}>Checking authentication...</Text>
      </SafeAreaView>
    );
  }

  // Don't render anything if not authenticated (will redirect)
  if (!user) {
    return null;
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>DSAExplorer</Text>
          {userName ? (
            <Text style={styles.welcomeText}>Welcome, {userName}</Text>
          ) : null}
        </View>
        <View style={styles.headerButtons}>
          <TouchableOpacity
            onPress={() => setShowBookmarks(!showBookmarks)}
            style={[styles.bookmarkToggle, showBookmarks && styles.bookmarkToggleActive]}
          >
            <FontAwesome 
              name="bookmark" 
              size={18} 
              color={showBookmarks ? "#4F46E5" : "#6B7280"} 
            />
            {isWeb && <Text style={styles.bookmarkToggleText}>Bookmarks</Text>}
          </TouchableOpacity>
          <TouchableOpacity
            onPress={handleLogout}
            style={[styles.logoutButton, isWeb && { cursor: 'pointer' }]}
            activeOpacity={0.7}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? (
              <ActivityIndicator size="small" color="#4F46E5" />
            ) : (
              <View style={styles.logoutContainer}>
                <Feather name="log-out" size={18} color="#6B7280" />
                {isWeb && <Text style={styles.logoutText}>Logout</Text>}
              </View>
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchInput}>
          <Feather name="search" size={20} color="#9CA3AF" style={styles.searchIcon} />
          <TextInput
            placeholder="Search algorithms..."
            style={styles.searchTextInput}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor="#9CA3AF"
          />
        </View>
      </View>

      {/* Category Filter - Updated for mobile */}
      <View style={styles.categoryContainer}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoryScrollContent}
        >
          {categories.map((item) => (
            <TouchableOpacity
              key={item}
              onPress={() => setSelectedCategory(item)}
              style={[
                styles.categoryPill,
                selectedCategory === item && styles.categoryPillActive,
              ]}
            >
              <Text style={[
                styles.categoryText,
                selectedCategory === item && styles.categoryTextActive
              ]}>
                {item}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Results Count */}
      <View style={styles.resultsContainer}>
        <Text style={styles.resultsText}>
          {filteredAlgorithms.length} {filteredAlgorithms.length === 1 ? 'algorithm' : 'algorithms'} found
          {selectedCategory !== 'All' ? ` in ${selectedCategory}` : ''}
          {searchQuery ? ` for "${searchQuery}"` : ''}
          {showBookmarks ? ' (Bookmarked)' : ''}
        </Text>
      </View>

      {/* Algorithm list */}
      <FlatList
        data={filteredAlgorithms}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        numColumns={isWeb ? effectiveColumns : 2}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <MaterialIcons name="search-off" size={48} color="#E5E7EB" />
            <Text style={styles.emptyText}>
              {showBookmarks 
                ? "No bookmarked algorithms found. Try bookmarking some first." 
                : "No algorithms found. Try a different search or category."}
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    paddingHorizontal: Platform.OS === 'web' ? 24 : 16,
    paddingTop: Platform.OS === 'ios' ? 0 : 16,
  },
  centerContent: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    color: '#6B7280',
    fontSize: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    marginTop: Platform.OS === 'web' ? 0 : 8,
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111827',
  },
  welcomeText: {
    color: '#6B7280',
    fontSize: 14,
    marginTop: 4,
  },
  logoutButton: {
    padding: 8,
  },
  logoutContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  logoutText: {
    color: '#6B7280',
    fontSize: 14,
  },
  bookmarkToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
  },
  bookmarkToggleActive: {
    backgroundColor: '#E0E7FF',
  },
  bookmarkToggleText: {
    color: '#6B7280',
    fontSize: 14,
  },
  searchContainer: {
    marginBottom: 16,
  },
  searchInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 50,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchTextInput: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
    paddingVertical: 12,
  },
  categoryContainer: {
    marginBottom: 16,
    maxHeight: 40,
  },
  categoryScrollContent: {
    paddingHorizontal: Platform.OS === 'web' ? 0 : 4,
  },
  categoryPill: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: 'transparent',
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  categoryPillActive: {
    backgroundColor: '#4F46E5',
    borderColor: '#4F46E5',
  },
  categoryText: {
    color: '#6B7280',
    fontSize: 14,
    fontWeight: '500',
  },
  categoryTextActive: {
    color: '#fff',
  },
  resultsContainer: {
    marginBottom: 16,
  },
  resultsText: {
    color: '#6B7280',
    fontSize: 14,
  },
  listContent: {
    paddingBottom: Platform.OS === 'web' ? 40 : 24,
  },
  card: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardCategory: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  bookmarkButton: {
    padding: 4,
  },
  cardContent: {
    padding: 16,
    alignItems: 'center',
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardIcon: {
    width: 32,
    height: 32,
    resizeMode: 'contain',
    tintColor: '#4F46E5',
  },
  cardTitle: {
    color: '#111827',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 16,
  },
  cardButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  cardButtonText: {
    color: '#4F46E5',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  emptyText: {
    color: '#9CA3AF',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 12,
    lineHeight: 24,
  },
});