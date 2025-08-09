from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class ForecastDemand(CodedTool):
    """Return a dummy demand forecast for a product."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        product = args.get("product", "item")
        # Dummy forecast value
        return {"product": product, "forecast": 100}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(args, sly_data)


class OptimizeInventory(CodedTool):
    """Provide a simple reorder recommendation."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        forecast = float(args.get("forecast", 0))
        current_stock = float(args.get("current_stock", 0))
        lead_time = float(args.get("lead_time", 0))
        reorder = max(forecast - current_stock + lead_time, 0)
        return {"reorder_quantity": reorder}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(args, sly_data)


class CreatePurchaseOrder(CodedTool):
    """Create a placeholder purchase order."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        product = args.get("product", "item")
        quantity = args.get("quantity", 0)
        return f"Purchase order created for {quantity} units of {product}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        return self.invoke(args, sly_data)


class CheckStock(CodedTool):
    """Report on-hand stock levels."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        product = args.get("product", "item")
        on_hand = sly_data.get("inventory", {}).get(product, 0)
        return {"product": product, "on_hand": on_hand}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(args, sly_data)


class GenerateReport(CodedTool):
    """Generate a simple text report."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        report_type = args.get("report_type", "summary")
        return f"Generated {report_type} report"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        return self.invoke(args, sly_data)
