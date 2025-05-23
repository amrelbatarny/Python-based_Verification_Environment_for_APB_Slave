"""
File   : SequenceLibrary.py
Author : Amr El Batarny
Brief  : Contains various APB sequences for generating different types of APB transactions during simulation.
"""

import cocotb
import vsc
from cocotb.triggers import RisingEdge, FallingEdge
from pyuvm import uvm_sequence, uvm_report_object, ConfigDB, uvm_root, path_t, check_t, access_e
from pyuvm import UVMConfigItemNotFound
from SequenceItemVSC import ApbSeqItemVSC
from SequenceItemCR import ApbSeqItemCR
from SequenceItemCCVG import ApbSeqItemCCVG
from APB_seq_itemMod import APB_seq_item
from pyquesta import SVConduit
from APB_utils import APBType

class ApbBaseSequence(uvm_sequence, uvm_report_object):
	
	def seq_print(self, msg: str):
		uvm_root().logger.info(msg)
	
	async def pre_body(self):
		self.seq_print("Entered sequence pre_body")
		
		# Get the number of transactions value from ConfigDB
		try:
			self.txn_num = ConfigDB().get(None, "", "NUM_TRANSACTIONS")
		except UVMConfigItemNotFound:
			self.txn_num = 300 # default value for number of transactions

		# Get the register model handle from ConfigDB
		self.ral = ConfigDB().get(None, "", "REGISTER_MODEL")
		self.map = self.ral.def_map
		
		# Read the coverage-mode flag from the ConfigDB (default to False)
		try:
			self.sv_rand_en = ConfigDB().get(None, "", "ENABLE_SV_RANDOMIZATION")
		except UVMConfigItemNotFound:
			self.sv_rand_en = False
		
		self.item = ApbSeqItemVSC.create("item")


	async def body(self):
		raise UVMNotImplemented  


##############################################################################
# Specialized APB Test Sequences
##############################################################################

class ApbTestAllSequence(ApbBaseSequence):

	async def body(self):
		# Receive transactions from the chosen randomization backend:
		# - If SV randomization is disabled, randomize PyVSC-based item
		# - Otherwise, get a randomized item from SystemVerilog via SVConduit.get()
		if self.sv_rand_en == False:
			self.seq_print("=====================================================================================================")
			self.seq_print(f"{self.get_type_name()}: Sending {self.txn_num} {self.item.get_type_name()} transactions ...")
			self.seq_print("=====================================================================================================")

			for _ in range(self.txn_num):
				await self.start_item(self.item)
				self.item.randomize()
				await self.finish_item(self.item)
		else:
			self.seq_print("=====================================================================================================")
			self.seq_print(f"{self.get_type_name()}: Sending {self.txn_num} SVConduit transactions")
			self.seq_print("=====================================================================================================")

			for _ in range(self.txn_num):
				await self.start_item(self.item)
				item_sv = SVConduit.get(APB_seq_item)
				self.item.data = item_sv.data
				self.item.type = APBType.WRITE if item_sv.type_sv else APBType.READ
				self.item.addr = item_sv.addr
				self.item.strobe = item_sv.strobe
				await self.finish_item(self.item)

class ApbWriteSequence(ApbBaseSequence):

	async def body(self):
		for _ in range(self.txn_num):
			await self.start_item(self.item)
			with self.item.randomize_with() as it:
				vsc.dist(it.type, [
					vsc.weight(APBType.WRITE, 95),
					vsc.weight(APBType.READ, 5)
					])
			await self.finish_item(self.item)

class ApbReadSequence(ApbBaseSequence):

	async def body(self):
		for _ in range(self.txn_num):
			await self.start_item(self.item)
			with self.item.randomize_with() as it:
				vsc.dist(it.type, [
					vsc.weight(APBType.WRITE, 5),
					vsc.weight(APBType.READ, 95)
					])
			await self.finish_item(self.item)

class ApbRegSequence(ApbBaseSequence):

	async def body(self):
		# Write Operations:
		status = await self.ral.reg_INPUT_DATA_REG.write(0x1F2C9A0D, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_MEM_CTRL_REG.write(0x87A20C05, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_DMA_CTRL_REG.write(0xF1C3422A, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_INT_CTRL_REG.write(0xABCDEF12, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_DEV_ID_REG.write(0x34578967, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_ADC_CTRL_REG.write(0x78954806, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_VOLTAGE_CTRL_REG.write(0x2347AEBC, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_TEMP_SENSOR_REG.write(0x218390FA, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_GPIO_DATA_REG.write(0x9C86AB3D, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_TIMER_COUNT_REG.write(0xF7D89A2C, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_DAC_OUTPUT_REG.write(0x908CD2AB, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_SYS_STATUS_REG.write(0x12345678, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_CLK_CONFIG_REG.write(0x15A4B8CD, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_SYS_CTRL_REG.write(0xA560F4CB, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_DBG_CTRL_REG.write(0xEA5B7C12, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		status = await self.ral.reg_OUTPUT_DATA_REG.write(0xC9D287A3, self.map, path_t.FRONTDOOR, check_t.NO_CHECK)

		# Read Operations:
		(status, rdata) = await self.ral.reg_INPUT_DATA_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_MEM_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_DMA_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_INT_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_DEV_ID_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_ADC_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_VOLTAGE_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_TEMP_SENSOR_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_GPIO_DATA_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_TIMER_COUNT_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_DAC_OUTPUT_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_SYS_STATUS_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_CLK_CONFIG_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_SYS_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_DBG_CTRL_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
		(status, rdata) = await self.ral.reg_OUTPUT_DATA_REG.read(self.map, path_t.FRONTDOOR, check_t.NO_CHECK)
