import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Platform, Text, StatusBar } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import React from 'react';

import { Home } from 'components/Home';
import { Login } from 'components/Login';
import { Register } from 'components/Register';
import { Main } from 'components/Main';
import { LinearSearch } from 'components/LinearSearch';
import { BinarySearch } from 'components/BinarySearch';
import { BubbleSort } from 'components/BubbleSort';
import { SelectionSort } from 'components/SelectionSort';
import { InsertionSort } from 'components/InsertionSort';
import { MergeSort } from 'components/MergeSort';
import { QuickSort } from 'components/QuickSort';
import { OneDArrayOperations } from 'components/OneDArrayOperations';
import { TwoDArrayOperations } from 'components/TwoDArrayOperations';
import { StringManipulations } from 'components/StringManipulations';
import { SinglyLinkedList } from 'components/SinglyLinkedList';
import { DoubleLinkedList } from 'components/DoubleLinkedList';
import { CircularSingleLinkedList } from 'components/CircularSingleLinkedList';
import { CircularDoublyLinkedListVisualizer } from 'components/CircularDoublyLinkedList';
import { StackVisualizer } from 'components/Stack';
import { QueueVisualizer } from 'components/Queue';
import { InorderTraversalVisualizer } from 'components/InorderTraversal';
import { PreorderTraversalVisualizer } from 'components/PreorderTraversal';
import { PostorderTraversalVisualizer } from 'components/PostorderTraversal';
import { BFSVisualizer } from 'components/BFS';
import { DFSVisualizer } from 'components/DFS';

import { AuthProvider, useAuth } from './AuthContext';
import './global.css';

const Stack = createNativeStackNavigator();

// Screens available without login
function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: Platform.OS === 'ios' }}>
      <Stack.Screen name="Home" component={Home} />
      <Stack.Screen name="Login" component={Login} />
      <Stack.Screen name="Register" component={Register} />
    </Stack.Navigator>
  );
}

// Screens available only after login
function AppStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: Platform.OS === 'ios',
        contentStyle: { backgroundColor: '#be4141ff' },
      }}
    >
      <Stack.Screen name="Main" component={Main} />
      <Stack.Screen name="LinearSearch" component={LinearSearch} />
      <Stack.Screen name="BinarySearch" component={BinarySearch} />
      <Stack.Screen name="BubbleSort" component={BubbleSort} />
      <Stack.Screen name="SelectionSort" component={SelectionSort} />
      <Stack.Screen name="InsertionSort" component={InsertionSort} />
      <Stack.Screen name="MergeSort" component={MergeSort} />
      <Stack.Screen name="QuickSort" component={QuickSort} />
      <Stack.Screen name="OneDArrayOperations" component={OneDArrayOperations} />
      <Stack.Screen name="TwoDArrayOperations" component={TwoDArrayOperations} />
      <Stack.Screen name="StringManipulations" component={StringManipulations} />
      <Stack.Screen name="SinglyLinkedList" component={SinglyLinkedList} />
      <Stack.Screen name="DoubleLinkedList" component={DoubleLinkedList} />
      <Stack.Screen name="CircularSingleLinkedList" component={CircularSingleLinkedList} />
      <Stack.Screen name="CircularDoublyLinkedList" component={CircularDoublyLinkedListVisualizer} />
      <Stack.Screen name="Stack" component={StackVisualizer} />
      <Stack.Screen name="Queue" component={QueueVisualizer} />
      <Stack.Screen name="InorderTraversal" component={InorderTraversalVisualizer} />
      <Stack.Screen name="PreorderTraversal" component={PreorderTraversalVisualizer} />
      <Stack.Screen name="PostorderTraversal" component={PostorderTraversalVisualizer} />
      <Stack.Screen name="BFSTraversal" component={BFSVisualizer} />
      <Stack.Screen name="DFS" component={DFSVisualizer} />
    </Stack.Navigator>
  );
}

// Switch stack based on auth state
function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) return <Text>Loading...</Text>;

  return user ? <AppStack /> : <AuthStack />;
}

export default function App() {
  return (
    <SafeAreaProvider style={{ flex: 1 }}>
      <AuthProvider>
        <NavigationContainer
          linking={{
            prefixes: ['http://localhost:3000', 'https://your-app-domain.com'],
            config: {
              screens: {
                Home: 'home',
                Login: 'login',
                Register: 'register',
                Main: 'main',
                LinearSearch: 'linear-search',
                BinarySearch: 'binary-search',
                BubbleSort: 'bubble-sort',
                SelectionSort: 'selection-sort',
                InsertionSort: 'insertion-sort',
                MergeSort: 'merge-sort',
                QuickSort: 'quick-sort',
                OneDArrayOperations: '1d-array',
                TwoDArrayOperations: '2d-array',
                StringManipulations: 'string',
                SinglyLinkedList: 'singly-linked-list',
                DoubleLinkedList: 'double-linked-list',
                CircularSingleLinkedList: 'circular-single-linked-list',
                CircularDoublyLinkedList: 'circular-doubly-linked-list',
                Stack: 'stack',
                Queue: 'queue',
                InorderTraversal: 'inorder',
                PreorderTraversal: 'preorder',
                PostorderTraversal: 'postorder',
                BFSTraversal: 'bfs',
                DFS: 'dfs',
              },
            },
          }}
        >
          <RootNavigator />
        </NavigationContainer>
        <StatusBar />
      </AuthProvider>
    </SafeAreaProvider>
  );
}
