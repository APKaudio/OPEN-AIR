<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Switch___OpenClose
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.Relay701 = New System.Windows.Forms.Button()
        Me.Relay702 = New System.Windows.Forms.Button()
        Me.Relay703 = New System.Windows.Forms.Button()
        Me.Relay704 = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'Relay701
        '
        Me.Relay701.Location = New System.Drawing.Point(50, 34)
        Me.Relay701.Name = "Relay701"
        Me.Relay701.Size = New System.Drawing.Size(164, 23)
        Me.Relay701.TabIndex = 0
        Me.Relay701.Text = "Bench Relay 701"
        Me.Relay701.UseVisualStyleBackColor = True
        '
        'Relay702
        '
        Me.Relay702.Location = New System.Drawing.Point(50, 75)
        Me.Relay702.Name = "Relay702"
        Me.Relay702.Size = New System.Drawing.Size(164, 23)
        Me.Relay702.TabIndex = 1
        Me.Relay702.Text = "Bench Relay 702"
        Me.Relay702.UseVisualStyleBackColor = True
        '
        'Relay703
        '
        Me.Relay703.Location = New System.Drawing.Point(50, 138)
        Me.Relay703.Name = "Relay703"
        Me.Relay703.Size = New System.Drawing.Size(164, 23)
        Me.Relay703.TabIndex = 2
        Me.Relay703.Text = "Bench Relay 703"
        Me.Relay703.UseVisualStyleBackColor = True
        '
        'Relay704
        '
        Me.Relay704.Location = New System.Drawing.Point(50, 167)
        Me.Relay704.Name = "Relay704"
        Me.Relay704.Size = New System.Drawing.Size(164, 23)
        Me.Relay704.TabIndex = 3
        Me.Relay704.Text = "Bench Relay 704"
        Me.Relay704.UseVisualStyleBackColor = True
        '
        'Switch___OpenClose
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(284, 261)
        Me.Controls.Add(Me.Relay704)
        Me.Controls.Add(Me.Relay703)
        Me.Controls.Add(Me.Relay702)
        Me.Controls.Add(Me.Relay701)
        Me.Name = "Switch___OpenClose"
        Me.Text = "Switch___OpenClose"
        Me.ResumeLayout(False)

    End Sub

    Friend WithEvents Relay701 As Button
    Friend WithEvents Relay702 As Button
    Friend WithEvents Relay703 As Button
    Friend WithEvents Relay704 As Button
End Class
