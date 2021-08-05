import torch.nn as nn

# 1x1 convolution
def conv1x1(in_channels, out_channels, stride, padding):
    model = nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, padding=padding),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    )
    return model


# 3x3 convolution
def conv3x3(in_channels, out_channels, stride, padding):
    model = nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=padding),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    )
    return model

###########################################################################
# Question 1 : Implement the "bottle neck building block" part.
# Hint : Think about difference between downsample True and False. How we make the difference by code?
class ResidualBlock(nn.Module): #nn.Module클래스 상속
    """
       Residual Network의 bottleneck 구조
       - down 파라미터는 down 블록을 통과하였을 때, feature map의 크기가 줄어드는 지의 여부의 불리언 값 입니다.
           - True인 경우 stride = 2가 되어 크기가 반으로 줄어듭니다.
       - 경우에 따라서 채널의 갯수가 달라 더해지지 않는 경우가 있는데, 이럴 때는 차원을 맞춰 주는 1x1 conv를 추가하여
         입력의 채널을 출력의 채널과 같게 만들어 줍니다.
        """
    def __init__(self, in_channels, middle_channels, out_channels, downsample=False): # 사용할 네트워크 모델들을 정의
        super(ResidualBlock, self).__init__() #부모의 init메소드 실행
        self.downsample = downsample

        if self.downsample: # 이미지의 사이즈를 stride를 이용하여 줄이는 경우의 코드
            self.layer = nn.Sequential(
                ##########################################
                ############## fill in here (20 points)
                # Hint : use these functions (conv1x1, conv3x3)
                conv1x1(in_channels, middle_channels, stride=2, padding=0),
                conv3x3(middle_channels, middle_channels, stride=1, padding=1),# To maintain image size, I should set padding as 1 to 3x3 kernel.
                conv1x1(middle_channels, out_channels, stride=1, padding=0)
                #########################################
            )
            self.downsize = conv1x1(in_channels, out_channels, 2, 0)

        else: ###여기에 지금 문제 있음. tensor(차원의수)가 다름
            self.layer = nn.Sequential(
                ##########################################
                ############# fill in here (20 points)
                conv1x1(in_channels, middle_channels, 1, 0),
                conv3x3(middle_channels, middle_channels, 1, 1), # To maintain image size, I should set padding as 1 to 3x3 kernel.
                conv1x1(middle_channels, out_channels, 1, 0)
                #########################################
            )
            self.make_equal_channel = conv1x1(in_channels, out_channels, 1, 0)

    def forward(self, x): # 모델들을 사용하여 순전파 로직 구현. residual block
        if self.downsample:
            out = self.layer(x)
            x = self.downsize(x) # identity mapping. out과 size를 맞춰주어야 한다.
            return out + x
        else: ### 문제 있음
            out = self.layer(x)
            if x.size() is not out.size():
                x = self.make_equal_channel(x) # identity mapping
            return out + x
###########################################################################



###########################################################################
# Question 2 : Implement the "class, ResNet50_layer4" part.
# Understand ResNet architecture and fill in the blanks below. (25 points)
# (blank : #blank#, 1 points per blank )
# Implement the code.
class ResNet50_layer4(nn.Module):
    def __init__(self, num_classes=10):# Hint : How many classes in Cifar-10 dataset?
        super(ResNet50_layer4, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(stride=2, kernel_size=7, in_channels=3, padding=3, out_channels=64),
                # Hint : Through this conv-layer, the input image size is halved.
                #        Consider stride, kernel size, padding and input & output channel sizes.
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(stride=2, kernel_size=3, padding=0)
        )
        self.layer2 = nn.Sequential(
            ResidualBlock(in_channels=64, middle_channels=64, out_channels=256, downsample=False),
            ResidualBlock(in_channels=256, middle_channels=64, out_channels=256, downsample=False),
            ResidualBlock(in_channels=256, middle_channels=64, out_channels=256, downsample=True)
        )
        self.layer3 = nn.Sequential(
            ##########################################
            ############# fill in here (20 points)
            ####### you can refer to the 'layer2' above
            #########################################
            ResidualBlock(in_channels=256, middle_channels=128, out_channels=512, downsample=False),
            ResidualBlock(in_channels=512, middle_channels=128, out_channels=512, downsample=False),
            ResidualBlock(in_channels=512, middle_channels=128, out_channels=512, downsample=False),
            ResidualBlock(in_channels=512, middle_channels=128, out_channels=512, downsample=True)
        )
        self.layer4 = nn.Sequential(
            ##########################################
            ############# fill in here (20 points)
            ####### you can refer to the 'layer2' above
            #########################################
            ResidualBlock(in_channels=512, middle_channels=256, out_channels=1024, downsample=False),
            ResidualBlock(in_channels=1024, middle_channels=256, out_channels=1024, downsample=False),
            ResidualBlock(in_channels=1024, middle_channels=256, out_channels=1024, downsample=False),
            ResidualBlock(in_channels=1024, middle_channels=256, out_channels=1024, downsample=False),
            ResidualBlock(in_channels=1024, middle_channels=256, out_channels=1024, downsample=False),
            ResidualBlock(in_channels=1024, middle_channels=256, out_channels=1024, downsample=False)
        )
        self.fc = nn.Linear(1024, 10) # Hint : Think about the reason why fc layer is needed
        self.avgpool = nn.AvgPool2d(kernel_size=7, stride=2, padding=3)
        # To maintain image size, I should set padding as 3.
        # To decrease the size of image, I gave stride 2.

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight.data)
            elif isinstance(m, nn.Conv2d):
                nn.init.xavier_uniform_(m.weight.data)

    def forward(self, x):

        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.avgpool(out)
        out = out.view(out.size()[0], -1)
        out = self.fc(out)

        return out
###########################################################################