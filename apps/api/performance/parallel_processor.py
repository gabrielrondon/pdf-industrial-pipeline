"""
Parallel Processing Coordinator - Stage 6 Performance

Gerencia processamento paralelo para melhorar throughput:
- Pool de workers assíncronos
- Distribuição de tarefas
- Monitoramento de recursos
- Balanceamento de carga
- Recuperação de falhas
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue, Empty
import threading
import multiprocessing as mp

logger = logging.getLogger(__name__)

@dataclass
class WorkerStats:
    """Estatísticas de um worker"""
    worker_id: str
    status: str
    tasks_completed: int
    tasks_failed: int
    cpu_usage: float
    memory_usage_mb: float
    last_activity: datetime
    uptime_seconds: float

@dataclass
class ProcessorStats:
    """Estatísticas do processador paralelo"""
    active_workers: int
    total_workers: int
    queued_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_task_duration: float
    cpu_usage: float
    memory_usage_mb: float
    throughput_per_minute: float

class TaskResult:
    """Resultado de uma tarefa"""
    def __init__(self, success: bool, result: Any = None, error: str = None):
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.now()

class ParallelTask:
    """Tarefa para processamento paralelo"""
    def __init__(self, task_id: str, func: Callable, args: tuple = (), kwargs: dict = None):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.created_at = datetime.now()
        self.priority = 0

class ParallelProcessor:
    """
    Coordenador de processamento paralelo
    """
    
    def __init__(self, 
                 max_workers: int = None,
                 use_processes: bool = False,
                 enable_monitoring: bool = True):
        self.max_workers = max_workers or mp.cpu_count()
        self.use_processes = use_processes
        self.enable_monitoring = enable_monitoring
        
        # Executores
        self.executor = None
        self.task_queue = Queue()
        self.result_store = {}
        
        # Estatísticas
        self.stats = {
            "completed_tasks": 0,
            "failed_tasks": 0,
            "start_time": datetime.now(),
            "task_times": []
        }
        
        # Workers e monitoramento
        self.worker_stats = {}
        self.is_running = False
        self.monitor_thread = None
        
        self._initialize_executor()
    
    def _initialize_executor(self):
        """Inicializa o executor"""
        try:
            if self.use_processes:
                self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
                logger.info(f"ProcessPoolExecutor inicializado com {self.max_workers} workers")
            else:
                self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
                logger.info(f"ThreadPoolExecutor inicializado com {self.max_workers} workers")
                
            self.is_running = True
            
            if self.enable_monitoring:
                self._start_monitoring()
                
        except Exception as e:
            logger.error(f"Erro ao inicializar executor: {e}")
    
    def _start_monitoring(self):
        """Inicia thread de monitoramento"""
        self.monitor_thread = threading.Thread(target=self._monitor_workers, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoramento de workers iniciado")
    
    def _monitor_workers(self):
        """Monitora workers continuamente"""
        while self.is_running:
            try:
                # Coletar estatísticas do sistema
                process = psutil.Process()
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                
                # Atualizar estatísticas globais
                current_time = datetime.now()
                uptime = (current_time - self.stats["start_time"]).total_seconds()
                
                # Calcular throughput
                total_tasks = self.stats["completed_tasks"] + self.stats["failed_tasks"]
                throughput = (total_tasks / (uptime / 60)) if uptime > 0 else 0
                
                # Log periódico
                if total_tasks > 0 and total_tasks % 100 == 0:
                    logger.info(f"Processamento: {total_tasks} tarefas, "
                              f"throughput: {throughput:.1f}/min, "
                              f"CPU: {cpu_percent:.1f}%")
                
                time.sleep(30)  # Monitor a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(60)
    
    async def submit_task(self, task: ParallelTask) -> str:
        """
        Submete tarefa para processamento paralelo
        
        Args:
            task: Tarefa para processar
            
        Returns:
            ID da tarefa submetida
        """
        try:
            # Adicionar à fila
            self.task_queue.put(task)
            
            # Processar tarefa
            future = self.executor.submit(self._execute_task, task)
            
            # Armazenar referência
            self.result_store[task.task_id] = {
                "future": future,
                "task": task,
                "submitted_at": datetime.now()
            }
            
            logger.debug(f"Tarefa submetida: {task.task_id}")
            return task.task_id
            
        except Exception as e:
            logger.error(f"Erro ao submeter tarefa {task.task_id}: {e}")
            raise
    
    def _execute_task(self, task: ParallelTask) -> TaskResult:
        """Executa uma tarefa"""
        start_time = time.time()
        
        try:
            result = task.func(*task.args, **task.kwargs)
            
            # Atualizar estatísticas
            execution_time = time.time() - start_time
            self.stats["completed_tasks"] += 1
            self.stats["task_times"].append(execution_time)
            
            # Manter apenas últimas 1000 medições
            if len(self.stats["task_times"]) > 1000:
                self.stats["task_times"] = self.stats["task_times"][-1000:]
            
            logger.debug(f"Tarefa {task.task_id} concluída em {execution_time:.2f}s")
            return TaskResult(True, result)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.stats["failed_tasks"] += 1
            
            logger.error(f"Erro na tarefa {task.task_id}: {e}")
            return TaskResult(False, None, str(e))
    
    async def get_result(self, task_id: str, timeout: float = None) -> Optional[TaskResult]:
        """
        Obtém resultado de uma tarefa
        
        Args:
            task_id: ID da tarefa
            timeout: Timeout em segundos
            
        Returns:
            Resultado da tarefa ou None se não encontrada
        """
        if task_id not in self.result_store:
            return None
        
        try:
            future = self.result_store[task_id]["future"]
            result = future.result(timeout=timeout)
            
            # Limpar referência
            del self.result_store[task_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter resultado {task_id}: {e}")
            return TaskResult(False, None, str(e))
    
    async def submit_batch(self, tasks: List[ParallelTask]) -> List[str]:
        """
        Submete lote de tarefas
        
        Args:
            tasks: Lista de tarefas
            
        Returns:
            Lista de IDs das tarefas
        """
        task_ids = []
        
        for task in tasks:
            task_id = await self.submit_task(task)
            task_ids.append(task_id)
        
        logger.info(f"Lote de {len(tasks)} tarefas submetido")
        return task_ids
    
    async def wait_for_batch(self, task_ids: List[str], timeout: float = None) -> List[TaskResult]:
        """
        Aguarda conclusão de lote de tarefas
        
        Args:
            task_ids: IDs das tarefas
            timeout: Timeout total em segundos
            
        Returns:
            Lista de resultados
        """
        results = []
        start_time = time.time()
        
        for task_id in task_ids:
            remaining_timeout = None
            if timeout:
                elapsed = time.time() - start_time
                remaining_timeout = max(0, timeout - elapsed)
            
            result = await self.get_result(task_id, remaining_timeout)
            results.append(result)
        
        logger.info(f"Lote de {len(task_ids)} tarefas processado")
        return results
    
    def get_stats(self) -> ProcessorStats:
        """Retorna estatísticas do processador"""
        try:
            # Estatísticas básicas
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
            total_tasks = self.stats["completed_tasks"] + self.stats["failed_tasks"]
            
            # Throughput
            throughput = (total_tasks / (uptime / 60)) if uptime > 0 else 0
            
            # Duração média das tarefas
            avg_duration = 0
            if self.stats["task_times"]:
                avg_duration = sum(self.stats["task_times"]) / len(self.stats["task_times"])
            
            # Recursos do sistema
            process = psutil.Process()
            cpu_usage = process.cpu_percent()
            memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
            
            return ProcessorStats(
                active_workers=self._get_active_workers(),
                total_workers=self.max_workers,
                queued_tasks=self.task_queue.qsize(),
                completed_tasks=self.stats["completed_tasks"],
                failed_tasks=self.stats["failed_tasks"],
                avg_task_duration=round(avg_duration, 3),
                cpu_usage=round(cpu_usage, 2),
                memory_usage_mb=round(memory_usage, 2),
                throughput_per_minute=round(throughput, 2)
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return ProcessorStats(0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def _get_active_workers(self) -> int:
        """Conta workers ativos"""
        if not self.executor:
            return 0
        
        try:
            # Para ThreadPoolExecutor
            if hasattr(self.executor, '_threads'):
                return len([t for t in self.executor._threads if t.is_alive()])
            
            # Para ProcessPoolExecutor
            if hasattr(self.executor, '_processes'):
                return len([p for p in self.executor._processes.values() if p.is_alive()])
            
            return 0
            
        except Exception:
            return 0
    
    def shutdown(self, wait: bool = True):
        """Desliga o processador"""
        self.is_running = False
        
        if self.executor:
            self.executor.shutdown(wait=wait)
            logger.info("Processador paralelo desligado")
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do processador"""
        try:
            stats = self.get_stats()
            
            # Determinar status
            status = "healthy"
            if stats.cpu_usage > 90:
                status = "overloaded"
            elif stats.failed_tasks > (stats.completed_tasks * 0.1):
                status = "degraded"
            elif not self.is_running:
                status = "stopped"
            
            return {
                "status": status,
                "active_workers": stats.active_workers,
                "total_workers": stats.total_workers,
                "queued_tasks": stats.queued_tasks,
                "success_rate": round(
                    (stats.completed_tasks / (stats.completed_tasks + stats.failed_tasks) * 100)
                    if (stats.completed_tasks + stats.failed_tasks) > 0 else 100, 2
                ),
                "throughput_per_minute": stats.throughput_per_minute,
                "avg_task_duration": stats.avg_task_duration
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Singleton instance
parallel_processor = ParallelProcessor()

# Funções utilitárias para uso comum
async def process_jobs_parallel(job_ids: List[str], 
                              processor_func: Callable,
                              max_concurrent: int = None) -> List[Any]:
    """
    Processa lista de jobs em paralelo
    
    Args:
        job_ids: Lista de IDs de jobs
        processor_func: Função para processar cada job
        max_concurrent: Máximo de jobs simultâneos
        
    Returns:
        Lista de resultados
    """
    if max_concurrent and len(job_ids) > max_concurrent:
        # Processar em lotes
        results = []
        for i in range(0, len(job_ids), max_concurrent):
            batch = job_ids[i:i + max_concurrent]
            batch_results = await _process_batch(batch, processor_func)
            results.extend(batch_results)
        return results
    else:
        return await _process_batch(job_ids, processor_func)

async def _process_batch(job_ids: List[str], processor_func: Callable) -> List[Any]:
    """Processa um lote de jobs"""
    tasks = []
    
    for job_id in job_ids:
        task = ParallelTask(
            task_id=f"job_{job_id}",
            func=processor_func,
            args=(job_id,)
        )
        tasks.append(task)
    
    # Submeter tarefas
    task_ids = await parallel_processor.submit_batch(tasks)
    
    # Aguardar resultados
    results = await parallel_processor.wait_for_batch(task_ids, timeout=300)
    
    return [r.result for r in results if r.success] 