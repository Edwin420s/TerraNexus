import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList } from 'react-native';

export const TasksScreen: React.FC = () => {
  const [tasks, setTasks] = useState([
    { id: '1', title: 'Scout maize whorls for armyworm', priority: 'high', completed: false },
    { id: '2', title: 'Inspect greenhouse drip filter for clogging', priority: 'medium', completed: false },
    { id: '3', title: 'Check solar pump inverter battery terminals', priority: 'low', completed: true },
  ]);

  const toggleTask = (id: string) => {
    setTasks(
      tasks.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Offline Task Checklist</Text>
      <Text style={styles.subtitle}>Check off tasks offline; mutations sync automatically.</Text>

      <FlatList
        data={tasks}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.taskItem, item.completed && styles.taskCompleted]}
            onPress={() => toggleTask(item.id)}
          >
            <View style={[styles.checkbox, item.completed && styles.checkboxChecked]}>
              {item.completed && <Text style={styles.checkmark}>✓</Text>}
            </View>
            <View style={{ flex: 1 }}>
              <Text style={[styles.taskTitle, item.completed && styles.taskTitleCompleted]}>
                {item.title}
              </Text>
              <Text style={styles.taskMeta}>Priority: {item.priority.toUpperCase()}</Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 16 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#0f172a' },
  subtitle: { fontSize: 12, color: '#64748b', marginTop: 4, marginBottom: 16 },
  taskItem: { backgroundColor: '#ffffff', borderRadius: 12, padding: 16, marginBottom: 10, flexDirection: 'row', alignItems: 'center', gap: 12, elevation: 1 },
  taskCompleted: { backgroundColor: '#f1f5f9', opacity: 0.8 },
  checkbox: { width: 22, height: 22, borderRadius: 6, borderWidth: 2, borderColor: '#cbd5e1', alignItems: 'center', justifyContent: 'center' },
  checkboxChecked: { backgroundColor: '#10b981', borderColor: '#10b981' },
  checkmark: { color: '#ffffff', fontSize: 12, fontWeight: 'bold' },
  taskTitle: { fontSize: 14, fontWeight: '700', color: '#1e293b' },
  taskTitleCompleted: { textDecorationLine: 'line-through', color: '#94a3b8' },
  taskMeta: { fontSize: 11, color: '#64748b', marginTop: 2 },
});
