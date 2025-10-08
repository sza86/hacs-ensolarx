from __future__ import annotations
import asyncio, struct, logging
from typing import List

_LOGGER = logging.getLogger(__name__)

class ModbusError(Exception):
    pass

class ModbusTcpClient:
    def __init__(self, host: str, port: int, unit_id: int = 1, timeout: float = 3.0) -> None:
        self._host = host
        self._port = port
        self._unit = unit_id
        self._timeout = timeout
        self._reader = None
        self._writer = None
        self._tid = 0

    async def connect(self) -> None:
        if self._writer:
            return
        _LOGGER.debug("Connecting Modbus TCP to %s:%s (unit=%s)", self._host, self._port, self._unit)
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self._host, self._port), timeout=self._timeout
        )

    async def close(self) -> None:
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = None
        self._writer = None

    async def _send_pdu(self, pdu: bytes) -> bytes:
        if not self._writer or not self._reader:
            await self.connect()
        self._tid = (self._tid + 1) & 0xFFFF
        length = len(pdu) + 1  # + unit
        mbap = struct.pack(">HHHB", self._tid, 0, length, self._unit)
        self._writer.write(mbap + pdu)
        await self._writer.drain()

        hdr = await asyncio.wait_for(self._reader.readexactly(7), timeout=self._timeout)
        tid, _, length, unit = struct.unpack(">HHHB", hdr)
        pdu_len = length - 1
        data = await asyncio.wait_for(self._reader.readexactly(pdu_len), timeout=self._timeout)
        if data and (data[0] & 0x80):
            code = data[1] if len(data) > 1 else 0
            raise ModbusError(f"Exception from device (function={data[0]&0x7F}, code={code})")
        return data

    async def read_coils(self, address: int, count: int) -> List[bool]:
        pdu = struct.pack(">BHH", 1, address, count)
        data = await self._send_pdu(pdu)
        byte_count = data[1]
        raw = data[2:2+byte_count]
        bits = []
        for i in range(count):
            b = raw[i // 8]
            bits.append(bool((b >> (i % 8)) & 1))
        return bits

    async def read_holding_registers(self, address: int, count: int) -> List[int]:
        pdu = struct.pack(">BHH", 3, address, count)
        data = await self._send_pdu(pdu)
        byte_count = data[1]
        regs = list(struct.unpack(f">{byte_count//2}H", data[2:2+byte_count]))
        return regs

    async def read_input_registers(self, address: int, count: int) -> List[int]:
        pdu = struct.pack(">BHH", 4, address, count)
        data = await self._send_pdu(pdu)
        byte_count = data[1]
        regs = list(struct.unpack(f">{byte_count//2}H", data[2:2+byte_count]))
        return regs
