"""
Health Monitoring - Stage 6 Performance

Sistema de monitoramento de saúde do pipeline:
- Health checks de todos os componentes
- Alertas e notificações
- Dashboard de status
- Métricas de disponibilidade
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status de saúde"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Resultado de um health check"""
    component: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any] = None

@dataclass
class SystemStatus:
    """Status geral do sistema"""
    overall_status: HealthStatus
    components: List[HealthCheck]
    uptime_seconds: float
    total_checks: int
    healthy_checks: int
    last_updated: datetime

class HealthMonitor:
    """
    Monitor de saúde do sistema
    """
    
    def __init__(self):
        self.components = {}
        self.check_history = {}
        self.start_time = datetime.now()
        self.check_interval = 60  # segundos
        self.running = False
        logger.info("HealthMonitor inicializado")
    
    def register_component(self, name: str, check_function, critical: bool = True):
        """
        Registra um componente para monitoramento
        
        Args:
            name: Nome do componente
            check_function: Função que retorna Dict com status
            critical: Se é crítico para o sistema
        """
        self.components[name] = {
            "check_function": check_function,
            "critical": critical,
            "last_check": None,
            "consecutive_failures": 0
        }
        self.check_history[name] = []
        logger.info(f"Componente registrado: {name} (crítico: {critical})")
    
    def _perform_check(self, component_name: str) -> HealthCheck:
        """Executa health check de um componente"""
        start_time = time.time()
        
        try:
            component = self.components[component_name]
            check_function = component["check_function"]
            
            # Executar check
            result = check_function()
            response_time_ms = (time.time() - start_time) * 1000
            
            # Interpretar resultado
            if isinstance(result, dict):
                status_str = result.get("status", "unknown")
                message = result.get("message", "No message")
                details = result
            else:
                status_str = "healthy" if result else "unhealthy"
                message = "Check passed" if result else "Check failed"
                details = {"raw_result": result}
            
            # Converter status
            try:
                status = HealthStatus(status_str.lower())
            except ValueError:
                status = HealthStatus.UNKNOWN
                message = f"Unknown status: {status_str}"
            
            # Atualizar contadores
            if status == HealthStatus.HEALTHY:
                component["consecutive_failures"] = 0
            else:
                component["consecutive_failures"] += 1
            
            health_check = HealthCheck(
                component=component_name,
                status=status,
                message=message,
                response_time_ms=round(response_time_ms, 2),
                timestamp=datetime.now(),
                details=details
            )
            
            component["last_check"] = health_check
            self.check_history[component_name].append(health_check)
            
            # Manter apenas últimos 100 checks
            if len(self.check_history[component_name]) > 100:
                self.check_history[component_name] = self.check_history[component_name][-100:]
            
            logger.debug(f"Health check {component_name}: {status.value} ({response_time_ms:.2f}ms)")
            return health_check
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                component=component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                response_time_ms=round(response_time_ms, 2),
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
            
            # Atualizar componente
            if component_name in self.components:
                self.components[component_name]["consecutive_failures"] += 1
                self.components[component_name]["last_check"] = health_check
                self.check_history[component_name].append(health_check)
            
            logger.error(f"Health check {component_name} falhou: {e}")
            return health_check
    
    def check_all_components(self) -> SystemStatus:
        """Executa health check de todos os componentes"""
        checks = []
        
        for component_name in self.components.keys():
            check = self._perform_check(component_name)
            checks.append(check)
        
        # Determinar status geral
        overall_status = self._calculate_overall_status(checks)
        
        # Estatísticas
        uptime = (datetime.now() - self.start_time).total_seconds()
        healthy_count = len([c for c in checks if c.status == HealthStatus.HEALTHY])
        
        system_status = SystemStatus(
            overall_status=overall_status,
            components=checks,
            uptime_seconds=uptime,
            total_checks=len(checks),
            healthy_checks=healthy_count,
            last_updated=datetime.now()
        )
        
        logger.info(f"System health check: {overall_status.value} "
                   f"({healthy_count}/{len(checks)} healthy)")
        
        return system_status
    
    def _calculate_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Calcula status geral baseado nos checks"""
        if not checks:
            return HealthStatus.UNKNOWN
        
        # Verificar componentes críticos
        critical_checks = []
        non_critical_checks = []
        
        for check in checks:
            component_info = self.components.get(check.component, {})
            if component_info.get("critical", True):
                critical_checks.append(check)
            else:
                non_critical_checks.append(check)
        
        # Se algum crítico está unhealthy, sistema é unhealthy
        critical_unhealthy = any(c.status == HealthStatus.UNHEALTHY for c in critical_checks)
        if critical_unhealthy:
            return HealthStatus.UNHEALTHY
        
        # Se algum crítico está degraded, sistema é degraded
        critical_degraded = any(c.status == HealthStatus.DEGRADED for c in critical_checks)
        if critical_degraded:
            return HealthStatus.DEGRADED
        
        # Se todos críticos estão healthy, verificar não-críticos
        all_critical_healthy = all(c.status == HealthStatus.HEALTHY for c in critical_checks)
        if all_critical_healthy:
            # Se muitos não-críticos estão com problema, degraded
            if non_critical_checks:
                unhealthy_non_critical = len([c for c in non_critical_checks if c.status == HealthStatus.UNHEALTHY])
                if unhealthy_non_critical / len(non_critical_checks) > 0.5:
                    return HealthStatus.DEGRADED
            
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def get_component_status(self, component_name: str) -> Optional[HealthCheck]:
        """Retorna último status de um componente"""
        return self.components.get(component_name, {}).get("last_check")
    
    def get_component_history(self, component_name: str, limit: int = 50) -> List[HealthCheck]:
        """Retorna histórico de um componente"""
        history = self.check_history.get(component_name, [])
        return history[-limit:] if limit else history
    
    def get_availability_stats(self, component_name: str = None, hours: int = 24) -> Dict[str, Any]:
        """Calcula estatísticas de disponibilidade"""
        since = datetime.now() - timedelta(hours=hours)
        
        if component_name:
            components_to_check = [component_name]
        else:
            components_to_check = list(self.components.keys())
        
        stats = {}
        
        for comp_name in components_to_check:
            history = self.check_history.get(comp_name, [])
            recent_checks = [c for c in history if c.timestamp >= since]
            
            if not recent_checks:
                stats[comp_name] = {"availability_percent": 0, "total_checks": 0}
                continue
            
            healthy_checks = len([c for c in recent_checks if c.status == HealthStatus.HEALTHY])
            availability = (healthy_checks / len(recent_checks)) * 100
            
            avg_response_time = sum(c.response_time_ms for c in recent_checks) / len(recent_checks)
            
            stats[comp_name] = {
                "availability_percent": round(availability, 2),
                "total_checks": len(recent_checks),
                "healthy_checks": healthy_checks,
                "avg_response_time_ms": round(avg_response_time, 2),
                "last_status": recent_checks[-1].status.value if recent_checks else "unknown"
            }
        
        return stats
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        alerts = []
        
        for comp_name, component in self.components.items():
            consecutive_failures = component.get("consecutive_failures", 0)
            last_check = component.get("last_check")
            
            if consecutive_failures >= 3:  # 3 falhas consecutivas
                alerts.append({
                    "type": "consecutive_failures",
                    "component": comp_name,
                    "severity": "high" if component.get("critical") else "medium",
                    "message": f"{comp_name} has {consecutive_failures} consecutive failures",
                    "since": last_check.timestamp if last_check else None
                })
            
            if last_check and last_check.response_time_ms > 5000:  # > 5 segundos
                alerts.append({
                    "type": "slow_response",
                    "component": comp_name,
                    "severity": "medium",
                    "message": f"{comp_name} is responding slowly ({last_check.response_time_ms:.0f}ms)",
                    "since": last_check.timestamp
                })
        
        return alerts
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do próprio monitor"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        total_components = len(self.components)
        components_with_recent_checks = len([
            c for c in self.components.values()
            if c.get("last_check") and 
            (datetime.now() - c["last_check"].timestamp).total_seconds() < 300  # 5 minutos
        ])
        
        return {
            "status": "healthy" if components_with_recent_checks == total_components else "degraded",
            "uptime_seconds": uptime,
            "registered_components": total_components,
            "components_checked_recently": components_with_recent_checks,
            "total_checks_performed": sum(len(history) for history in self.check_history.values())
        }

# Singleton instance
health_monitor = HealthMonitor()

# Função para registrar componentes facilmente
def register_health_check(name: str, critical: bool = True):
    """
    Decorador para registrar health check
    
    Usage:
        @register_health_check("redis_cache", critical=True)
        def check_redis():
            return {"status": "healthy", "message": "Redis OK"}
    """
    def decorator(func):
        health_monitor.register_component(name, func, critical)
        return func
    return decorator 