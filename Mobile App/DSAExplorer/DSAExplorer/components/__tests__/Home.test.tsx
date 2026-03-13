// import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { Home } from '../Home';
import { useNavigation } from '@react-navigation/native';

// Mock useNavigation
const mockedNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: mockedNavigate,
  }),
}));

describe('Home Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Home />);
    
    expect(getByText('DSAExplorer')).toBeTruthy();
    expect(getByText('Master Data Structures & Algorithms with interactive visualizations.')).toBeTruthy();
    expect(getByText('Get Started')).toBeTruthy();
  });

  it('navigates to Login when Get Started is pressed', () => {
    const { getByText } = render(<Home />);
    const getStartedButton = getByText('Get Started');
    
    fireEvent.press(getStartedButton);
    
    expect(mockedNavigate).toHaveBeenCalledWith('Login');
  });
});
