// AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type User = {
  username: string;
  accessToken: string;
};

type AuthContextType = {
  user: User | null;
  login: (userData: User) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore user session on app start
  useEffect(() => {
    const loadUser = async () => {
      try {
        const accessToken = await AsyncStorage.getItem('accessToken');
        const username = await AsyncStorage.getItem('username');
        
        if (accessToken && username) {
          setUser({ username, accessToken });
        }
      } catch (e) {
        console.error('Failed to load user:', e);
      }
      setLoading(false);
    };
    loadUser();
  }, []);

  const login = async (userData: User) => {
    setUser(userData);
    await AsyncStorage.setItem('accessToken', userData.accessToken);
    await AsyncStorage.setItem('username', userData.username);
  };

  const logout = async () => {
    setUser(null);
    await AsyncStorage.removeItem('user');
    await AsyncStorage.removeItem('accessToken');
    await AsyncStorage.removeItem('refreshToken');
    await AsyncStorage.removeItem('username');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};