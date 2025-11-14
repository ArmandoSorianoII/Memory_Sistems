import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import platform
import subprocess
import json
from datetime import datetime
import numpy as np

class MemoryMonitor:
    def __init__(self):
        self.fig, self.axes = plt.subplots(2, 3, figsize=(16, 10))
        self.fig.suptitle('Monitor de Sistemas de Memoria - Windows', fontsize=16, fontweight='bold')
        
        # Historial de datos para gráficos temporales
        self.ram_history = []
        self.swap_history = []
        self.cache_history = []
        self.time_points = []
        self.max_points = 50
        
    def get_ram_info(self):
        """Obtiene información de la memoria RAM principal"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total / (1024**3),  # GB
            'available': mem.available / (1024**3),
            'used': mem.used / (1024**3),
            'percent': mem.percent,
            'free': mem.free / (1024**3)
        }
    
    def get_cache_info(self):
        """Obtiene información de memoria caché (aproximación en Windows)"""
        mem = psutil.virtual_memory()
        # En Windows, cached + buffers se aproxima al caché del sistema
        return {
            'cached': mem.cached / (1024**3) if hasattr(mem, 'cached') else 0,
            'buffers': mem.buffers / (1024**3) if hasattr(mem, 'buffers') else 0,
            'total_cache': (mem.cached + mem.buffers) / (1024**3) if hasattr(mem, 'cached') else 0
        }
    
    def get_virtual_memory_info(self):
        """Obtiene información de memoria virtual (swap)"""
        swap = psutil.swap_memory()
        return {
            'total': swap.total / (1024**3),
            'used': swap.used / (1024**3),
            'free': swap.free / (1024**3),
            'percent': swap.percent
        }
    
    def get_disk_info(self):
        """Obtiene información de discos (para detectar RAID)"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total / (1024**3),
                    'used': usage.used / (1024**3),
                    'free': usage.free / (1024**3),
                    'percent': usage.percent
                }
                disks.append(disk_info)
            except:
                pass
        return disks
    
    def plot_ram(self, ax):
        """Grafica información de RAM principal"""
        ram = self.get_ram_info()
        
        ax.clear()
        ax.set_title('Memoria RAM Principal', fontweight='bold')
        
        # Gráfico de barras
        categories = ['Usada', 'Disponible']
        values = [ram['used'], ram['available']]
        colors = ['#e74c3c', '#2ecc71']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel('GB')
        ax.set_ylim(0, ram['total'] * 1.1)
        
        # Añadir valores en las barras
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f} GB\n({val/ram["total"]*100:.1f}%)',
                   ha='center', va='bottom', fontweight='bold')
        
        # Información adicional
        info_text = f'Total: {ram["total"]:.2f} GB\nUso: {ram["percent"]:.1f}%'
        ax.text(0.98, 0.98, info_text, transform=ax.transAxes,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def plot_ram_timeline(self, ax):
        """Grafica línea temporal del uso de RAM"""
        ram = self.get_ram_info()
        
        # Actualizar historial
        self.ram_history.append(ram['percent'])
        if len(self.ram_history) > self.max_points:
            self.ram_history.pop(0)
        
        ax.clear()
        ax.set_title('Historial de Uso de RAM', fontweight='bold')
        ax.plot(self.ram_history, color='#e74c3c', linewidth=2, marker='o', markersize=3)
        ax.set_ylabel('Uso (%)')
        ax.set_xlabel('Tiempo')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.fill_between(range(len(self.ram_history)), self.ram_history, alpha=0.3, color='#e74c3c')
    
    def plot_cache(self, ax):
        """Grafica información de caché"""
        cache = self.get_cache_info()
        ram = self.get_ram_info()
        
        ax.clear()
        ax.set_title('Memoria Caché del Sistema', fontweight='bold')
        
        # Gráfico circular
        total_cache = cache['total_cache']
        other = ram['total'] - total_cache
        
        if total_cache > 0:
            sizes = [total_cache, other]
            labels = [f'Caché\n{total_cache:.2f} GB', f'Otra RAM\n{other:.2f} GB']
            colors = ['#3498db', '#ecf0f1']
            explode = (0.1, 0)
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                  startangle=90, explode=explode)
        else:
            ax.text(0.5, 0.5, 'Información de caché\nno disponible en Windows',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        ax.axis('equal')
    
    def plot_virtual_memory(self, ax):
        """Grafica memoria virtual (swap)"""
        swap = self.get_virtual_memory_info()
        
        ax.clear()
        ax.set_title('Memoria Virtual (Archivo de Paginación)', fontweight='bold')
        
        if swap['total'] > 0:
            # Gráfico de barras horizontales
            categories = ['Libre', 'Usada']
            values = [swap['free'], swap['used']]
            colors = ['#2ecc71', '#f39c12']
            
            bars = ax.barh(categories, values, color=colors, alpha=0.7, edgecolor='black')
            ax.set_xlabel('GB')
            ax.set_xlim(0, swap['total'] * 1.1)
            
            # Añadir valores
            for bar, val in zip(bars, values):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{val:.2f} GB ({val/swap["total"]*100:.1f}%)',
                       ha='left', va='center', fontweight='bold', fontsize=10)
            
            info_text = f'Total: {swap["total"]:.2f} GB\nUso: {swap["percent"]:.1f}%'
            ax.text(0.98, 0.02, info_text, transform=ax.transAxes,
                   verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        else:
            ax.text(0.5, 0.5, 'No hay archivo de\npaginación configurado',
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
    
    def plot_swap_timeline(self, ax):
        """Grafica línea temporal del uso de swap"""
        swap = self.get_virtual_memory_info()
        
        # Actualizar historial
        self.swap_history.append(swap['percent'])
        if len(self.swap_history) > self.max_points:
            self.swap_history.pop(0)
        
        ax.clear()
        ax.set_title('Historial de Memoria Virtual', fontweight='bold')
        
        if swap['total'] > 0:
            ax.plot(self.swap_history, color='#f39c12', linewidth=2, marker='s', markersize=3)
            ax.set_ylabel('Uso (%)')
            ax.set_xlabel('Tiempo')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            ax.fill_between(range(len(self.swap_history)), self.swap_history, alpha=0.3, color='#f39c12')
        else:
            ax.text(0.5, 0.5, 'No hay swap configurado',
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
    
    def plot_disks(self, ax):
        """Grafica información de discos"""
        disks = self.get_disk_info()
        
        ax.clear()
        ax.set_title('Almacenamiento en Disco (RAID/Volúmenes)', fontweight='bold')
        
        if disks:
            disk_names = [d['device'][:10] for d in disks[:5]]  # Primeros 5 discos
            disk_usage = [d['percent'] for d in disks[:5]]
            
            colors_disk = ['#e74c3c' if u > 80 else '#f39c12' if u > 60 else '#2ecc71' 
                          for u in disk_usage]
            
            bars = ax.barh(disk_names, disk_usage, color=colors_disk, alpha=0.7, edgecolor='black')
            ax.set_xlabel('Uso (%)')
            ax.set_xlim(0, 100)
            
            # Añadir valores y tamaños
            for i, (bar, disk) in enumerate(zip(bars, disks[:5])):
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                       f'{width:.1f}% ({disk["used"]:.1f}/{disk["total"]:.1f} GB)',
                       ha='left', va='center', fontsize=9)
        else:
            ax.text(0.5, 0.5, 'No se detectaron discos',
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
        
        ax.invert_yaxis()
    
    def update(self, frame):
        """Actualiza todos los gráficos"""
        try:
            self.plot_ram(self.axes[0, 0])
            self.plot_ram_timeline(self.axes[0, 1])
            self.plot_cache(self.axes[0, 2])
            self.plot_virtual_memory(self.axes[1, 0])
            self.plot_swap_timeline(self.axes[1, 1])
            self.plot_disks(self.axes[1, 2])
            
            plt.tight_layout()
        except Exception as e:
            print(f"Error actualizando gráficos: {e}")
    
    def run(self):
        """Inicia el monitor"""
        print("=== Monitor de Sistemas de Memoria ===")
        print(f"Sistema: {platform.system()} {platform.release()}")
        print("Presiona Ctrl+C para detener\n")
        
        # Animación que actualiza cada 2 segundos
        anim = FuncAnimation(self.fig, self.update, interval=2000, cache_frame_data=False)
        plt.show()

if __name__ == "__main__":
    try:
        monitor = MemoryMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("\nMonitor detenido por el usuario")
    except Exception as e:
        print(f"Error: {e}")
        print("\nAsegúrate de tener instaladas las dependencias:")
        print("pip install psutil matplotlib")