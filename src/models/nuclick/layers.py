import torch
import torch.nn as nn

bn_axis = 1


class Conv_Bn_Relu(nn.Module):
    def __init__(
            self,
            in_channels: int,
            out_channels: int = 32,
            kernelSize: tuple[int, int] | int = (3, 3),
            strds: tuple[int, int] | int = (1, 1),
            useBias: bool = False,
            dilatationRate: tuple[int, int] = (1, 1),
            actv: str | None = 'relu',
            doBatchNorm: bool = True
    ) -> None:
        super().__init__()
        if isinstance(kernelSize, int):
            kernelSize = (kernelSize, kernelSize)
        if isinstance(strds, int):
            strds = (strds, strds)

        self.conv_bn_relu = self.get_block(
            in_channels, out_channels, kernelSize, strds, useBias, dilatationRate, actv,
            doBatchNorm)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return self.conv_bn_relu(input)

    def get_block(
            self,
            in_channels: int,
            out_channels: int,
            kernelSize: tuple[int, int] | int,
            strds: tuple[int, int],
            useBias: bool,
            dilatationRate: tuple[int, int] | int,
            actv: str | None,
            doBatchNorm: bool
    ) -> nn.Sequential:

        layers = []

        conv1 = nn.Conv2d(
            in_channels=in_channels, out_channels=out_channels, kernel_size=kernelSize,
            stride=strds, dilation=dilatationRate, bias=useBias, padding='same',
            padding_mode='zeros')

        if actv == 'selu':
            # (Can't find 'lecun_normal' equivalent in PyTorch)
            torch.nn.init.xavier_normal_(conv1.weight)
        else:
            torch.nn.init.xavier_uniform_(conv1.weight)

        layers.append(conv1)

        if actv != 'selu' and doBatchNorm:
            layers.append(nn.BatchNorm2d(num_features=out_channels, eps=1.001e-5))

        if actv == 'relu':
            layers.append(nn.ReLU())
        elif actv == 'sigmoid':
            layers.append(nn.Sigmoid())
        elif actv == 'selu':
            layers.append(nn.SELU())

        block = nn.Sequential(*layers)
        return block


class Multiscale_Conv_Block(nn.Module):
    def __init__(
        self,
        in_channels: int,
        kernelSizes: list[tuple[int, int] | int],
        dilatationRates: list[int],
        out_channels: int = 32,
        strds: tuple[int, int] = (1, 1),
        actv: str = 'relu',
        useBias: bool = False,
        isDense: bool = True
    ) -> None:

        super().__init__()

        # Initialise conv blocks
        if isDense:
            self.conv_block_0 = Conv_Bn_Relu(
                in_channels=in_channels, out_channels=4 * out_channels, kernelSize=1,
                strds=strds, actv=actv, useBias=useBias)
            self.conv_block_5 = Conv_Bn_Relu(
                in_channels=in_channels, out_channels=out_channels, kernelSize=3,
                strds=strds, actv=actv, useBias=useBias)
        else:
            self.conv_block_0 = None  # type: ignore
            self.conv_block_5 = None  # type: ignore

        self.conv_block_1 = Conv_Bn_Relu(
            in_channels=in_channels, out_channels=out_channels,
            kernelSize=kernelSizes[0],
            strds=strds, actv=actv, useBias=useBias,
            dilatationRate=(dilatationRates[0],
                            dilatationRates[0]))

        self.conv_block_2 = Conv_Bn_Relu(
            in_channels=in_channels, out_channels=out_channels,
            kernelSize=kernelSizes[1],
            strds=strds, actv=actv, useBias=useBias,
            dilatationRate=(dilatationRates[1],
                            dilatationRates[1]))

        self.conv_block_3 = Conv_Bn_Relu(
            in_channels=in_channels, out_channels=out_channels,
            kernelSize=kernelSizes[2],
            strds=strds, actv=actv, useBias=useBias,
            dilatationRate=(dilatationRates[2],
                            dilatationRates[2]))

        self.conv_block_4 = Conv_Bn_Relu(
            in_channels=in_channels, out_channels=out_channels,
            kernelSize=kernelSizes[3],
            strds=strds, actv=actv, useBias=useBias,
            dilatationRate=(dilatationRates[3],
                            dilatationRates[3]))

    def forward(self, input_map: torch.Tensor) -> torch.Tensor:
        # If isDense == True
        if self.conv_block_0 is not None:
            conv0 = self.conv_block_0(input_map)
        else:
            conv0 = input_map  # type: ignore

        conv1 = self.conv_block_1(conv0)
        conv2 = self.conv_block_2(conv0)
        conv3 = self.conv_block_3(conv0)
        conv4 = self.conv_block_4(conv0)

        # (Not sure about bn_axis)
        output_map = torch.cat([conv1, conv2, conv3, conv4], dim=bn_axis)

        # If isDense == True
        if self.conv_block_5 is not None:
            output_map = self.conv_block_5(output_map)
            # (Not sure about bn_axis)
            output_map = torch.cat([input_map, output_map], dim=bn_axis)

        return output_map


class Residual_Conv(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int = 32,
        kernelSize: tuple[int, int] | int = (3, 3),
        strds: tuple[int, int] = (1, 1),
        actv: str = 'relu',
        useBias: bool = False,
        dilatationRate: tuple[int, int] = (1, 1)
    ) -> None:
        super().__init__()

        if actv == 'selu':
            self.conv_block_1 = Conv_Bn_Relu(
                in_channels, out_channels, kernelSize=kernelSize, strds=strds,
                actv='None', useBias=useBias, dilatationRate=dilatationRate,
                doBatchNorm=False)
            self.conv_block_2 = Conv_Bn_Relu(
                in_channels, out_channels, kernelSize=kernelSize, strds=strds,
                actv='None', useBias=useBias, dilatationRate=dilatationRate,
                doBatchNorm=False)
            self.activation = nn.SELU()
        else:
            self.conv_block_1 = Conv_Bn_Relu(
                in_channels, out_channels, kernelSize=kernelSize, strds=strds,
                actv='None', useBias=useBias, dilatationRate=dilatationRate,
                doBatchNorm=True)
            self.conv_block_2 = Conv_Bn_Relu(
                out_channels, out_channels, kernelSize=kernelSize, strds=strds,
                actv='None', useBias=useBias, dilatationRate=dilatationRate,
                doBatchNorm=True)

            if actv == 'relu':
                self.activation = nn.ReLU()

            if actv == 'sigmoid':
                self.activation = nn.Sigmoid()

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        conv1 = self.conv_block_1(input)
        conv2 = self.conv_block_2(conv1)

        out = torch.add(conv1, conv2)
        out = self.activation(out)
        return out
