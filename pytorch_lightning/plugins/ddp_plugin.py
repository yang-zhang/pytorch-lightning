from typing import List, Dict, Any

from pytorch_lightning.core.lightning import LightningModule
from pytorch_lightning.overrides.data_parallel import LightningDistributedDataParallel


class DDPPlugin(object):
    """
    Plugin to link a custom ddp implementation to any arbitrary accelerator.

    This plugin forwards all constructor arguments to `LightningDistributedDataParallel`,
    which in turn forwards all args to `DistributedDataParallel`.

    Example::

        class MyDDP(DDPPlugin):

            def configure_ddp(self, model, device_ids):
                model = MyDDPWrapper(model, device_ids)
                return model

        my_ddp = MyDDP()
        trainer = Trainer(accelerator='ddp_x', plugins=[my_ddp])
    """

    def __init__(self, **kwargs):
        self._ddp_kwargs: Dict[str, Any] = kwargs

    def configure_ddp(
        self, model: LightningModule, device_ids: List[int]
    ) -> LightningDistributedDataParallel:
        """
        Pass through all customizations from constructor to `LightningDistributedDataParallel`.
        Override to define a custom DDP implementation.

        .. note:: Only requirement is that your DDP implementation subclasses LightningDistributedDataParallel


        The default implementation is::

            def configure_ddp(self, model, device_ids):
                model = LightningDistributedDataParallel(
                    model, device_ids=device_ids, find_unused_parameters=True
                )
                return model

        Args:
            model: the lightningModule
            device_ids: the list of devices available

        Returns:
            the model wrapped in LightningDistributedDataParallel

        """
        # if unset, default `find_unused_parameters` `True`
        self._ddp_kwargs["find_unused_parameters"] = self._ddp_kwargs.get(
            "find_unused_parameters", True
        )
        model = LightningDistributedDataParallel(
            model,
            device_ids=device_ids,
            **self._ddp_kwargs,
        )
        return model

    def on_before_forward(self, model: LightningModule, *args):
        """
        Override to handle custom input to device logic. For DDP, no logic is required as this is handled internally
        within the DDP wrapper.

        Example::

            def on_before_forward(self, model, *args):
                batch, batch_idx = args
                return batch.to(model.device)

        Args:
            args: Inputs to the model.
            model: Model to train.
        Returns: args moved to correct device if needed.
        """
        return args
