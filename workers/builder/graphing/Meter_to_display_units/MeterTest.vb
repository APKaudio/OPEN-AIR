Public Class MeterTest


    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        Horizontal_Meter_With_Text1.Value_To_Display = TextBox.Text
    End Sub

    Private Sub TrackBar1_Scroll(sender As Object, e As EventArgs) Handles TrackBar1.Scroll
        Vertical_Meter1.Plot_V1 = TrackBar1.Value

    End Sub

    Private Sub TrackBar2_Scroll(sender As Object, e As EventArgs) Handles TrackBar2.Scroll
        Vertical_Meter1.Plot_V2 = TrackBar2.Value
    End Sub

    Private Sub TrackBar3_Scroll(sender As Object, e As EventArgs) Handles TrackBar3.Scroll
        Vertical_Meter1.Plot_V3 = TrackBar3.Value
    End Sub

    Private Sub TrackBar4_Scroll(sender As Object, e As EventArgs) Handles TrackBar4.Scroll
        Vertical_Meter1.Plot_V4 = TrackBar4.Value
    End Sub

    Private Sub MeterTest_Load(sender As Object, e As EventArgs) Handles MyBase.Resize
        Vertical_Meter1.Width = Me.Width / 4

    End Sub

    Private Sub MeterTest_Load_1(sender As Object, e As EventArgs) Handles MyBase.Load

    End Sub
End Class