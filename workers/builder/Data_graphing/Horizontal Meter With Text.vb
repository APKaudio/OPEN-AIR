
Public Class Horizontal_Meter_With_Text

    Private ValueReceived As Double
    Private TitleToDisplay As String

    Private MinValue As Integer
    Private MaxValue As Integer

    Public Property Value_To_Display() As Double
        Get
            Return ValueReceived

        End Get
        Set(value As Double)
            ValueReceived = value

            Label_Value.Text = ValueReceived
            UpdateGraph()
        End Set
    End Property


    Public Property Title_To_Display() As String
        Get
            Return TitleToDisplay
        End Get
        Set(value As String)
            TitleToDisplay = value
            Label_Title.Text = TitleToDisplay
            UpdateGraph()
        End Set
    End Property




    Private Sub Horizontal_Meter_With_Text_Load(sender As Object, e As EventArgs) Handles MyBase.Load

        BarGraphValueDec.Location.Y(1)

        BarGraphValueDec.Width = Me.Width
        BarGraphValueDec.Height = Me.Height / 2

        BarGraphValue1.Width = Me.Width
        BarGraphValue1.Height = Me.Height / 2



        UpdateGraph()
    End Sub

    Private Sub Horizontal_Meter_With_Text_MouseLeave(sender As Object, e As EventArgs) Handles Me.MouseLeave

    End Sub
    Private Sub UpdateGraph()

        Label_Title.Text = TitleToDisplay
        Label_Value.Text = ValueReceived








        BarGraphValue1.Value = Math.Truncate(ValueReceived)

        BarGraphValueDec.Value = (ValueReceived - Math.Truncate(ValueReceived)) * 100

        Label1.Text = Math.Truncate(ValueReceived)
        Labeldec.Text = (ValueReceived - Math.Truncate(ValueReceived)) * 100



    End Sub


    'Public Property Minimum() As Integer
    '    Get
    '        Return MinValue
    '    End Get
    '    Set(value As Integer)
    '        MinValue = value
    '        BarGraphValue10.Minimum = MinValue
    '        UpdateGraph()
    '    End Set
    'End Property

    'Public Property Maximum() As Integer
    '    Get
    '        Return MaxValue
    '    End Get
    '    Set(value As Integer)
    '        MaxValue = value
    '        BarGraphValue10.Maximum = MaxValue

    '        UpdateGraph()
    '    End Set
    'End Property


End Class




