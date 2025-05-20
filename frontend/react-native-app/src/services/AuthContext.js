import React, { createContext, useContext } from 'react';

// Create the Auth Context
const AuthContext = createContext({
  signIn: () => {},
  signOut: () => {},
  signUp: () => {},
});

// Provider component that wraps the app
export const AuthProvider = ({ children, value }) => {
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook for child components to access the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
