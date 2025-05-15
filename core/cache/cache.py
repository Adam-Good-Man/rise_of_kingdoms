import os
import json
import time
import hashlib
from typing import Any, Optional, Dict
from pathlib import Path

class Cache:
    def __init__(self, cache_dir: str = "temp/cache", max_age: int = 3600):
        """
        初始化缓存系统
        
        Args:
            cache_dir (str): 缓存文件存储目录
            max_age (int): 缓存最大有效期（秒），默认1小时
        """
        self._cache_dir = Path(cache_dir)
        self._max_age = max_age
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # 确保缓存目录存在
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_key(self, key: str) -> str:
        """
        生成缓存键
        
        Args:
            key: 原始键值
            
        Returns:
            str: 生成的缓存键
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        return hashlib.md5(key).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            Path: 缓存文件路径
        """
        return self._cache_dir / f"{key}.json"
    
    def _is_expired(self, timestamp: float) -> bool:
        """
        检查缓存是否过期
        
        Args:
            timestamp: 缓存时间戳
            
        Returns:
            bool: 是否过期
        """
        return time.time() - timestamp > self._max_age
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值（当缓存不存在或过期时返回）
            
        Returns:
            Any: 缓存值或默认值
        """
        cache_key = self._generate_key(key)
        
        # 首先检查内存缓存
        if cache_key in self._memory_cache:
            cache_data = self._memory_cache[cache_key]
            if not self._is_expired(cache_data['timestamp']):
                return cache_data['value']
            else:
                del self._memory_cache[cache_key]
        
        # 检查文件缓存
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                if not self._is_expired(cache_data['timestamp']):
                    # 更新内存缓存
                    self._memory_cache[cache_key] = cache_data
                    return cache_data['value']
                else:
                    cache_path.unlink()  # 删除过期缓存文件
            except (json.JSONDecodeError, IOError):
                cache_path.unlink()  # 删除损坏的缓存文件
        
        return default
    
    def set(self, key: str, value: Any, max_age: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 要缓存的值
            max_age: 可选的缓存有效期（秒），覆盖默认值
        """
        cache_key = self._generate_key(key)
        cache_data = {
            'value': value,
            'timestamp': time.time(),
            'max_age': max_age or self._max_age
        }
        
        # 更新内存缓存
        self._memory_cache[cache_key] = cache_data
        
        # 更新文件缓存
        try:
            with open(self._get_cache_path(cache_key), 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)
        except IOError:
            pass  # 忽略文件写入错误
    
    def delete(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        cache_key = self._generate_key(key)
        
        # 删除内存缓存
        self._memory_cache.pop(cache_key, None)
        
        # 删除文件缓存
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear(self) -> None:
        """
        清除所有缓存
        """
        # 清除内存缓存
        self._memory_cache.clear()
        
        # 清除文件缓存
        for cache_file in self._cache_dir.glob('*.json'):
            cache_file.unlink() 