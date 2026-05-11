#ifndef PACKET_HPP
#define PACKET_HPP

namespace lio_interface
{

struct data_
{
    double x;
    double y;
    double z;
    double roll;
    double pitch;
    double yaw;
    double rad_roll;
    double rad_pitch;
    double rad_yaw;
};

}   // namespace lio_interface

#endif  // PACKET_HPP