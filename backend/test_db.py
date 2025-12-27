import asyncio
import asyncpg

async def test_connection():
    # Try different host options
    hosts = [
        ('localhost', 5432),
        ('127.0.0.1', 5432),
        ('172.19.0.3', 5432),  # Container IP
    ]
    
    for host, port in hosts:
        try:
            print(f"Trying {host}:{port}...")
            conn = await asyncpg.connect(
                user='sniper_user',
                password='sniper_password',
                database='sniper_db',
                host=host,
                port=port,
                timeout=5
            )
            result = await conn.fetchval('SELECT 1')
            print(f"✅ Connection to {host}:{port} successful! Result: {result}")
            await conn.close()
            return
        except Exception as e:
            print(f"❌ {host}:{port} failed: {e}")
    
    # Try without password (for trust auth)
    print("\nTrying without password...")
    for host, port in hosts:
        try:
            print(f"Trying {host}:{port} (no password)...")
            conn = await asyncpg.connect(
                user='sniper_user',
                database='sniper_db',
                host=host,
                port=port,
                timeout=5
            )
            result = await conn.fetchval('SELECT 1')
            print(f"✅ Connection to {host}:{port} successful (no password)! Result: {result}")
            await conn.close()
            return
        except Exception as e:
            print(f"❌ {host}:{port} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
