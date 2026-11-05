import React, { useState } from 'react';
import { SafeAreaView, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ScoutingScreen } from './src/screens/ScoutingScreen';
import { TasksScreen } from './src/screens/TasksScreen';
import { PumpEmergencyScreen } from './src/screens/PumpEmergencyScreen';

export default function App() {
  const [activeTab, setActiveTab] = useState<'scouting' | 'tasks' | 'estop'>('scouting');

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <Text style={styles.brand}>TerraNexus Mobile</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>Offline-First</Text>
        </View>
      </View>

      <View style={styles.body}>
        {activeTab === 'scouting' && <ScoutingScreen />}
        {activeTab === 'tasks' && <TasksScreen />}
        {activeTab === 'estop' && <PumpEmergencyScreen />}
      </View>

      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabBtn, activeTab === 'scouting' && styles.tabBtnActive]}
          onPress={() => setActiveTab('scouting')}
        >
          <Text style={[styles.tabText, activeTab === 'scouting' && styles.tabTextActive]}>
            Scouting
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tabBtn, activeTab === 'tasks' && styles.tabBtnActive]}
          onPress={() => setActiveTab('tasks')}
        >
          <Text style={[styles.tabText, activeTab === 'tasks' && styles.tabTextActive]}>
            Tasks
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tabBtn, activeTab === 'estop' && styles.tabBtnActive]}
          onPress={() => setActiveTab('estop')}
        >
          <Text style={[styles.tabText, activeTab === 'estop' && styles.tabTextActive]}>
            E-Stop
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#ffffff' },
  header: { height: 56, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, borderBottomWidth: 1, borderBottomColor: '#f1f5f9' },
  brand: { fontSize: 16, fontWeight: '900', color: '#0f172a' },
  badge: { backgroundColor: '#ecfdf5', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  badgeText: { fontSize: 10, fontWeight: '700', color: '#059669' },
  body: { flex: 1 },
  tabBar: { height: 60, flexDirection: 'row', borderTopWidth: 1, borderTopColor: '#e2e8f0', backgroundColor: '#ffffff' },
  tabBtn: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  tabBtnActive: { borderTopWidth: 2, borderTopColor: '#10b981' },
  tabText: { fontSize: 12, fontWeight: '600', color: '#64748b' },
  tabTextActive: { color: '#10b981', fontWeight: '800' },
});
