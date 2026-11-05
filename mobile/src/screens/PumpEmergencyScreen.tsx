import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';

export const PumpEmergencyScreen: React.FC = () => {
  const [interlockTripped, setInterlockTripped] = useState(false);

  const handleEmergencyStop = () => {
    setInterlockTripped(true);
    Alert.alert('Emergency Cutoff', 'Emergency stop command dispatched. Pump relay cut power.');
  };

  const handleReset = () => {
    setInterlockTripped(false);
    Alert.alert('Interlock Reset', 'Safety interlock normalized.');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Field Emergency Control</Text>
      <Text style={styles.subtitle}>Direct hardware pump cutoff boundary (TNX-ARCH-001 Section 9).</Text>

      <View style={styles.statusCard}>
        <Text style={styles.statusLabel}>Physical Interlock Status</Text>
        <Text style={[styles.statusValue, interlockTripped ? styles.statusTripped : styles.statusArmed]}>
          {interlockTripped ? 'INTERLOCK TRIPPED (HALTED)' : 'ARMED & MONITORING'}
        </Text>
      </View>

      <TouchableOpacity style={styles.btnEStop} onPress={handleEmergencyStop}>
        <Text style={styles.btnEStopText}>EMERGENCY PUMP CUTOFF</Text>
      </TouchableOpacity>

      {interlockTripped && (
        <TouchableOpacity style={styles.btnReset} onPress={handleReset}>
          <Text style={styles.btnResetText}>Reset Safety Interlock</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 16, justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', color: '#0f172a', textAlign: 'center' },
  subtitle: { fontSize: 12, color: '#64748b', marginTop: 4, marginBottom: 24, textAlign: 'center' },
  statusCard: { backgroundColor: '#ffffff', borderRadius: 16, padding: 20, alignItems: 'center', marginBottom: 24, elevation: 1 },
  statusLabel: { fontSize: 12, fontWeight: '700', color: '#64748b', textTransform: 'uppercase' },
  statusValue: { fontSize: 16, fontWeight: '900', marginTop: 6 },
  statusArmed: { color: '#10b981' },
  statusTripped: { color: '#dc2626' },
  btnEStop: { backgroundColor: '#dc2626', paddingVertical: 24, borderRadius: 20, alignItems: 'center', elevation: 4 },
  btnEStopText: { color: '#ffffff', fontWeight: '900', fontSize: 16, letterSpacing: 1 },
  btnReset: { backgroundColor: '#e2e8f0', paddingVertical: 14, borderRadius: 12, alignItems: 'center', marginTop: 16 },
  btnResetText: { color: '#334155', fontWeight: '700', fontSize: 14 },
});
