Public Class Switch___OpenClose
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Relay701.Click
        '   Relay(701)


    End Sub

    Private Sub Relay702_Click(sender As Object, e As EventArgs) Handles Relay702.Click
        '    Relay(702)
    End Sub

    Private Sub Relay703_Click(sender As Object, e As EventArgs) Handles Relay703.Click
        '     Relay(703)
    End Sub

    Private Sub Relay704_Click(sender As Object, e As EventArgs) Handles Relay704.Click
        '            Relay(704)
    End Sub

    Private Sub Switch___OpenClose_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        '    SWRaddress()
        '    ReDim SwitcherModule.Relay(1000)
    End Sub




    '    Public Sub Relay(Relay As Integer)
    '        Try
    '            If SwitcherModule.Relay(Relay) = True Then
    '                SwitcherModule.SCIP.WriteString("Open " & Relay)
    '                SwitcherModule.Relay(Relay) = False
    '                Dim Relay_Button_Update() As Control = UserInterface.Controls.Find("Relay" & Relay, 1)
    '                Relay_Button_Update(0).BackColor = Color.Orange
    '            Else
    '                SwitcherModule.SCIP.WriteString("close " & Relay)
    '                SwitcherModule.Relay(Relay) = True
    '                Dim Relay_Button_Update() As Control = UserInterface.Controls.Find("Relay" & Relay, 1)
    '                Relay_Button_Update(0).BackColor = Color.Blue
    '            End If
    '        Catch ex As Exception
    '        End Try
    '    End Sub

End Class